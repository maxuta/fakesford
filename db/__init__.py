#!/usr/bin/env python3


if __name__ == '__main__':
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from mongo import connect
    from users import UserCollection

    from pymongo.errors import DuplicateKeyError
    from common.exc import AuthError

    db = connect('fakesford_test')
    print('all collections: %s' % db.list_collection_names())
    
    uc = UserCollection(db)
    uc._collection.drop()

    uc.add('maxuta', '123', '123', 'pupil', age=27, subjects=['a', 'b'])
    uc.add('kolya', '111', '111', 'tutor', age=26, subjects=['math'])

    print('all: %s' % list(uc.iter_all()))

    try:
        uc.add('maxuta', '555', '555', 'tutor', age=13, subjects=['aaaaa', 'bbbb'])
    except DuplicateKeyError:
        print('user maxuta already exists')

    maxuta = uc.get('maxuta')
    print('maxuta age: %s' % maxuta._conf['age'])

    try:
        uc.add('rita', '222', '333', 'tutor', age=26, subjects=['psy'])
    except AuthError:
        print('rita has problems with auth')


