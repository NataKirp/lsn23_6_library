from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from library.forms import BookForm, AuthorForm
from library.models import Book, Author

from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache

from library.services import BookService


class ReviewBookView(LoginRequiredMixin, View):
    def post(self, request, pk):
        book = get_object_or_404(Book, id=pk)

        if not request.user.has_perm('library.can_review_book'):
            return HttpResponseForbidden('У вас нет права для рецензирования книги.')

        book.review = request.POST.get('review')
        book.save()

        return redirect('library:book_detail', pk=pk)


class RecommendBookView(LoginRequiredMixin, View):
    def post(self, request, pk):
        book = get_object_or_404(Book, id=pk)

        if not request.user.has_perm('library.can_recommend_book'):
            return HttpResponseForbidden('У вас нет права для рекомендации книги.')

        book.recommend = True
        book.save()

        return redirect('library:book_detail', pk=pk)


class AuthorListView(ListView):
    model = Author
    template_name = 'library/authors_list.html'
    context_object_name = 'authors'

    def get_queryset(self):
        # альтернативный вариант см. в конце *
        queryset = cache.get('authors_queryset')
        if not queryset:
            queryset = super().get_queryset()
            cache.set('authors_queryset', queryset, 60 * 15)
        return queryset


class AuthorCreateView(CreateView):
    model = Author
    form_class = AuthorForm
    template_name = 'library/author_form.html'
    title = 'Добавить автора'
    success_url = reverse_lazy('library:authors_list')


class AuthorUpdateView(UpdateView):
    model = Author
    form_class = AuthorForm
    template_name = 'library/author_form.html'
    title = 'Редактировать автора'
    success_url = reverse_lazy('library:authors_list')


class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    # fields = ['title', 'publication_date', 'author']
    template_name = 'library/book_form.html'
    title = 'Добавить книгу'
    success_url = reverse_lazy('library:books_list')
    permission_required = 'library.add_book'


@method_decorator(cache_page(60 * 15), name='dispatch')
class BooksListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'library/books_list.html'
    context_object_name = 'books'
    # permission_required = 'library.view_book'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(publication_date__year__gt=2000)


# альтернативный вариант см. в конце **
# @method_decorator(cache_page(60 * 15), name='dispatch')
class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'library/book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        # Получаем стандартный контекст данных из родительского класса
        context = super().get_context_data(**kwargs)
        context['author_books_count'] = Book.objects.filter(author=self.object.author).count()
        # Получаем ID книги из объекта
        book_id = self.object.id
        # Добавляем в контекст средний рейтинг и статус популярности книги
        context['average_rating'] = BookService.calculate_average_rating(book_id)
        context['is_popular'] = BookService.is_popular(book_id)

        return context


class BookUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    # fields = ['title', 'publication_date', 'author']
    template_name = 'library/book_form.html'
    title = 'Редактировать книгу'
    success_url = reverse_lazy('library:books_list')
    permission_required = 'library.change_book'


class BookDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Book
    template_name = 'library/book_confirm_delete.html'
    success_url = reverse_lazy('library:books_list')
    permission_required = 'library.delete_book'


# * В предоставленном коде находится критическая логическая ошибка, из-за которой кеширование не работает,
# а нагрузка на базу данных только увеличивается. Главная проблема: кеширование «ленивого» QuerySet
# В Django метод super().get_queryset() возвращает объект QuerySet, который является ленивым.
# Это значит, что код программы не выполняет реальный запрос в базу данных (SQL) в момент вызова super().get_queryset().
# Он лишь создаёт объект-конструктор запроса. Когда выполняется инструкция:
# cache.set('authors_queryset', queryset, 60 * 15)
# в Django-кеш (Redis, Memcached или MemBase) сохраняется и сериализуется не результат запроса (список авторов),
# а сам ленивый объект QuerySet.
# Когда приходит следующий запрос, метод cache.get('authors_queryset') извлекает этот ленивый QuerySet из кеша.
# Затем Django начинает рендерить шаблон library/authors_list.html. Именно в этот момент — внутри шаблона при цикле for
# — QuerySet вычисляется и каждый раз делает новый запрос в базу данных. Кеш здесь становится абсолютно бесполезным
# и даже вредным (тратится время на сериализацию/десериализацию структуры запроса).
# Как исправить код правильно
# Чтобы кеширование заработало, QuerySet нужно принудительно вычислить (оценить) до сохранения в кеш, превратив его
# в реальный список объектов (Python list).
# Вариант 1. Кеширование списка объектов (Оптимально для get_queryset)
# Просто оберните super().get_queryset() в функцию list().
#
# class AuthorListView(ListView):
#     model = Author
#     template_name = 'library/authors_list.html'
#     context_object_name = 'authors'
#
#     def get_queryset(self):
#         # 1. Пытаемся достать уже готовый список из кеша
#         queryset = cache.get('authors_queryset')
#
#         if queryset is None:
#             # 2. Получаем ленивый QuerySet и принудительно превращаем его в список объектов
#             queryset = list(super().get_queryset())
#             # 3. Сохраняем в кеш чистый список на 15 минут
#             cache.set('authors_queryset', queryset, 60 * 15)
#
#         return queryset
#
# Важное примечание: При использовании list() вместо QuerySet встроенная пагинация ListView (paginate_by)
# перестанет работать эффективно на уровне БД, так как выгрузятся сразу все авторы. Если авторов очень много (тысячи),
# этот метод не подойдет.
#
# Вариант 2. Альтернатива через кеширование всего HTML (Template Caching)Если пагинация важна или авторов много,
# гораздо эффективнее и проще закешировать весь блок разметки прямо в шаблоне library/authors_list.html,
# оставив view стандартным.
#
# {% load cache %}
# {# Кешируем этот блок шаблона на 900 секунд (15 минут) #}
# {% cache 900 authors_list_fragment %}
#     {% for author in authors %}
#         <p>{{ author.name }}</p>
#     {% endfor %}
# {% endcache %}
#
# Дополнительные рекомендации по коду
# Проблема инвалидации кеша: Данные авторов будут отставать от базы на 15 минут. Если администратор добавит автора,
# пользователи увидят его не сразу. Рекомендуется сбрасывать кеш при изменении данных с помощью сигналов Django:
#
# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
#
# @receiver([post_save, post_delete], sender=Author)
# def clear_authors_cache(sender, **kwargs):
#     cache.delete('authors_queryset')
#
# Проверка на None: В исходном коде написано if not queryset:. Если из базы вернется пустой список авторов (база чистая),
# if not queryset сработает как True, и код будет дергать базу данных при каждом запросе, пытаясь переписать кеш.
# Правильнее проверять строго: if queryset is None:.
#
#
# ** В этом коде есть одна критическая архитектурная ошибка, связанная с кэшированием, и одна скрытая проблема
# производительности (лишний запрос), завязанная на ленивых объектах.
# Ошибка №1: Кэширование LoginRequiredMixin ломает безопасность
# Вы применили @method_decorator(cache_page(...), name='dispatch') ко всему классу. Метод dispatch управляет вообще всем
# жизненным циклом запроса, включая проверку авторизации.
# Что произойдет на практике:Первый (авторизованный) пользователь заходит на страницу книги. Django генерирует страницу
# и сохраняет её в кэш. Второй пользователь (аноним, который даже не вошел на сайт) заходит по этой же ссылке.
# Django видит закэшированную страницу на уровне dispatch и отдает её анониму, полностью проигнорировав LoginRequiredMixin!
# Анонимный пользователь увидит закрытые данные.
#
# Правило: Никогда не кэшируйте через cache_page представления, которые отдают разный контент для разных пользователей
# или защищены миксинами авторизации. cache_page отлично подходит только для публичных страниц.
#
# Проблема №2: Скрытый ленивый запрос в get_context_data
# Посмотрите на эту строчку:
# context['author_books_count'] = Book.objects.filter(author=self.object.author).count()
# Здесь self.object — это текущая книга. Когда вы вызываете self.object.author, Django видит, что объект author является
# связанным по ForeignKey. Так как изначально при получении книги автор не подгружался, Django в этот самый момент
# делает дополнительный ленивый запрос в таблицу авторов, чтобы просто взять его id. И только после этого выполняется
# запрос .count(). Это классический лишний шаг.
#
# Как сделать код идеальным?
#
# Вариант 1. Если страница одинаковая для всех, но нужна авторизация (Правильное кэширование)
# Если контент страницы не зависит от того, какой именно пользователь на нее смотрит (нет надписей вроде "Привет, Иван!"),
# то вместо кэширования всей страницы (cache_page) лучше закэшировать только тяжелые данные или сам шаблон (Fragment Caching).
# Но если вы хотите оставить именно постраничный кэш, нужно переписать код так, чтобы кэш учитывал статус пользователя
# или вынести кэширование внутрь метода get:
#
# class BookDetailView(LoginRequiredMixin, DetailView):
#     model = Book
#     template_name = 'library/book_detail.html'
#     context_object_name = 'book'
#
#     # Оптимизируем базовый запрос: сразу подгружаем ID автора,
#     # чтобы self.object.author_id не делал лишний запрос в БД
#     def get_queryset(self):
#         return super().get_queryset().select_related('author')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Используем self.object.author_id вместо self.object.author.
#         # Это исключает ленивый запрос к модели Author, так как ID уже есть в таблице Book!
#         context['author_books_count'] = Book.objects.filter(
#             author_id=self.object.author_id
#         ).count()
#         return context
#
#     # Кэшируем метод get ПОСЛЕ того, как LoginRequiredMixin проверил пользователя
#     @method_decorator(cache_page(60 * 15))
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
#
# Вариант 2. Если на странице есть личные данные пользователя (Кэширование шаблона)
#
# Если на странице отображается имя пользователя, его корзина или кнопка "Добавить в избранное", кэшировать всю страницу
# нельзя вообще. Уберите декоратор @method_decorator(cache_page...) из Python-кода и закэшируйте тяжелый блок прямо в
# HTML-шаблоне book_detail.html:html{% load cache %}
#
# <!-- Этот блок уникален для каждого, его не кэшируем -->
# <div class="user-header">Привет, {{ request.user.username }}</div>
#
# <!-- Кэшируем только информацию о книге и авторе на 15 минут -->
# <!-- 'book_cache' — имя кэша, book.id — динамический ключ -->
# {% cache 900 book_cache book.id %}
#     <h1>{{ book.title }}</h1>
#     <p>Всего книг у этого авт