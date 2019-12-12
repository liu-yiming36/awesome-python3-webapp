import test_orm
from test_models import User, Blog, Comment, next_id
import random

import asyncio
import string

# async def test():
#     await test_orm.creat_pool(user='www-data', password='www-data', databases='awesome')
#     u = User(name='Test', email='test@example.com', passwd='1234567890', image='about:blank')
#     await u.save()
#
# for x in test():
#     pass


# async def test(loop):
#     await test_orm.create_pool(loop, user='www-data', password='www-data', db='awesome')
#     u = User(name='test', email='test%s@example.com' % random.randint(0, 10000000), passwd='abc123456', image='about:blank')
#     await u.save()
#
#
# # 要运行协程,需要使用事件循环
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(test(loop))
#     print('Test finished.')
#     loop.close()



async def test(loop):
    await test_orm.create_pool(loop=loop, user='root', password='uu888888', db='awesome')

    u = User(name='Test', email='test1@example.com',
             password='1234567890', image='about:blank')
    print(u)
    print(type(u.email))
    await u.save()

loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.run_forever()

for x in test(loop):
    pass


# def random_email():
#     qq = random.randint(100000000, 999999999)
#     return str(qq)+'@qq.com'
#
# def random_name():
#     return ''.join(random.sample(string.ascii_letters, 5))
# async def test(loop):
#     await test_orm.create_pool(loop=loop, user='root', password='uu888888', db='awesome')
#
#     u = User(name='Rambo', email='1434284872@qq.com', passwd='123456', image='about:blank')
#
#     # #1. 测试插入方法，测试成功！
#     # for x in range(100):
#     #     u['id'] = next_id()
#     #     u['email'] = random_email()
#     #     u['name'] = random_name()
#     #     u['password'] = random_email()
#     #     await u.save()
#
#     # 2. 测试根据主键查询方法 ,测试成功
#     # u = await User.find('001575909452072380ded903edc451ba39c660680391145000')
#
#     # 3. 测试根据参数查询方法，测试陈宫
#     # u = await User.findAll(where='name like ?', args=['%a%'], orderBy='name asc', limit=(0, 10))
#
#     # 4. 测试findNumber方法，不知道这个方法有什么用，结果u = jZACD
#     # u = await User.findNumber('name')
#
#     # 5. 测试更新方法，测试成功
#     # u = await User.find('001575909452072380ded903edc451ba39c660680391145000')
#     # u['password'] = '123'
#     # await u.update()
#
#     # 6. 测试删除方法，测试成功
#     u = await User.find('001575909452072380ded903edc451ba39c660680391145000')
#     await u.remove()
#
#     print(u)
#
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(test(loop))
#     loop.run_forever()