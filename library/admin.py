from django.contrib import admin

from .models import Author, Book, Review


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date')
    search_fields = ('first_name', 'last_name')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'publication_date', 'author')
    list_filter = ('publication_date', 'author')
    search_fields = ('title', 'author__first_name', 'author__last_name')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'rating',)


# В Django, когда ты используешь двойное подчеркивание (__) в строках, как в 'author__first_name' и 'author__last_name',
# это называется "переход через отношения".
# В данном случае, author — это поле в модели Book, которое ссылается на другую модель Author.
# Поля first_name и last_name принадлежат модели Author.
# Когда ты указываешь author__first_name в search_fields, Django понимает, что ты хочешь искать книги по имени автора,
# переходя через связь между моделями Book и Author.
# Это как сказать: "Найди мне все книги, где имя автора начинается с...".
# Таким образом, двойное подчеркивание помогает Django "проваливаться" в связанные модели и работать с их полями.
# Это очень удобно, когда у тебя есть сложные связи между моделями, и ты хочешь делать запросы, которые учитывают эти связи.
#
# Двойные подчеркивания работают благодаря полям ForeignKey в моделях Django.
# Когда ты создаешь поле ForeignKey в одной модели, ты устанавливаешь связь с другой моделью.
# Это позволяет Django "переходить" от одной модели к другой через эту связь.
# Например, если у тебя есть модель Book с полем author, которое является ForeignKey на модель Author,
# то ты можешь использовать двойные подчеркивания, чтобы обращаться к полям модели Author через модель Book.
# Таким образом, author__first_name позволяет тебе получить доступ к полю first_name модели Author,
# связанной с конкретной книгой. Это делает работу со связанными данными в Django очень удобной и гибкой.