# coding:utf-8

from tinydb import Query, TinyDB, where


class Tdb:
    def __init__(self, path):
        db = TinyDB(path)
        self.Q = Query()
        self.t_certificate = db.table('certificate')
        self.t_relationship = db.table('relationship')

    def insert_cert(self, data):
        # String sid -> data['sid']
        # String secret -> data['secret']
        # int owner -> data['userid']
        self.t_certificate.insert({'sid': data['sid'],
                                   'secret': data['secret'],
                                   'owner': data['userid']})
        return True

    def delete_cert(self, data):
        self.t_certificate.remove((where('sid') == data['sid'])
                                  & (where('secret') == data['secret'])
                                  & (where('owner') == data['userid']))
        # 这里还需要删除 ship 下相关所有记录
        self.t_relationship.remove(where('sid') == data['sid'])
        # 检查
        if self.t_certificate.count((where('sid') == data['sid'])
                                    & (where('owner') == data['userid'])) == 0:

            return True
        return False

    def search_cert(self, data):
        result = self.t_certificate.search(where('owner') == data['userid'])
        return result

    def bind_cert(self, data):
        # 先检验是否存在此凭证
        if self.t_certificate.count((where('sid') == data['sid'])
                                     & (where('secret') == data['secret'])) != 0:
            # 检查是否已绑定过
            if self.t_relationship.count((where('sid') == data['sid'])
                                         & (where(('uid') == data['userid']))) == 0:
                # 绑定
                self.t_relationship.insert({'sid': data['sid'],
                                            'uid': data['userid']})
                return True
        return False

    def search_ship(self, data):
        return self.t_relationship.search(where('uid') == data['userid'])

    def unbind_cert(self, data):
        # 检验是否绑定此凭证
        if self.t_relationship.search((where('sid') == data['sid'])
                                      & (where('uid') == data['userid'])) != 0:
            self.t_relationship.remove((where('sid') == data['sid'])
                                       & (where('uid') == data['userid']))
            return True
        return False

    def find_ship_user(self, data):
        return self.t_relationship.search(where('sid') == data['sid'])

if __name__ == '__main__':
    tdb = Tdb('/Users/sariel.d/PycharmProjects/cspushboot/db.json')
    # tdb.insert_cert({'sid':'1', 'secret':'sss', 'userid':123})
    print tdb.delete_cert({'sid':'DZ949e18e8','secret':'f683c278-188a-5d4f-9238-e7024e880d7d','userid': 694231961})

