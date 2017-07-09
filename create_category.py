from catalog import db
from catalog.models import Category


def new_category(name):
    """
    new_category creates a new Category object given the name
    """
    category = Category()
    category.name = name
    return category


def main():
    # list of category names
    categories = [
        'Action', 'Comedy', 'Slice of Life',
        'Psychological', 'History', 'Supernatural',
        'Military', 'Romance', 'Science Fiction']
    for c in categories:
        db.session.add(new_category(c))
    # save all categories to db
    db.session.commit()


if __name__ == '__main__':
    main()
