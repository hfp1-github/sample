import os
import itertools
import glob

debugfilepaths = glob.glob("dbdir/*.txt")

def get_db_paths(dirpath='dbdir'):
    ret_paths = glob.glob(dirpath + "/*.txt")
    return ret_paths


class Textdb:
    def __init__(self, filepaths):
        # 検索は小文字データベースから行う(大文字小文字の区別が出来ないため)
        self.__db , self.path_idx_map = self.make_db2(filepaths)
        self.db_small = {n:[line.lower() for line in block] for n, block in self.db.items()}
    
    # 単一インデックスかiterableインデックスに対応
    def __getitem__(self, indexes):
        if type(indexes) != list:
            if hasattr(indexes, "__iter__"):
                indexes = list(indexes)
            else:
                indexes = [indexes]
        ret = [self.db[i] for i in indexes] 

        return ret

    def make_db(self, filepaths):
        if type(filepaths) != list:
            filepaths = [filepaths]


        """"
            改行3つで区切った文字列のリストを生成
        """

        delimiter = "\n"
        delim_threas = 3  # splitする\nが出てきた回数
        lines = []
        index = 0
        # ---dbリストを全て読み込み、結合
        for p in filepaths:
            with open(p, "r", encoding="utf-8") as f:
                _lines = f.readlines()

                # ---ファイル末尾に改行コードが足りない場合追加する処理
                lastlines = _lines[-min(delim_threas, len(_lines)):]
                for n, line in enumerate(reversed(lastlines)):
                    if line != delimiter:
                        break
                _lines += [delimiter] * (delim_threas - n)
                lines += _lines
        # ---改行コード×delim_threasでsplitする処理。
        ret_strlist = []  # return用
        dblen = len(lines)
        delimcount = 0  # \nが出てきた回数
        next_start_idx = 0  # 次回の開始インデックス
        for n, line in enumerate(lines):
            if line == delimiter:
                delimcount += 1
                if delimcount == delim_threas:  # \nがsplit回数出たらstr抽出、カウンタ類をリセット、更新
                    ret_strlist.append(lines[next_start_idx : n - delim_threas + 1])
                    next_start_idx = n + 1
                    delimcount = 0
            else:
                delimcount=0
            if n == dblen - 1:  # EOFなら残りを格納
                ret_strlist.append(lines[next_start_idx:])

        return ret_strlist


    def make_db2(self, filepath):
        """"
            改行3つで区切った文字列のリストを生成
        """

        # ------パスのテキストをdelimでブロック単位にsplit。インデックスでマッピング。
        delimiter = "\n"
        delim_threas = 3  # dlimiterがこの回数以上連続で出てきた場合、splitする。
        block_count = 0 # 抽出したブロックのカウンタ
        next_start_map_count = 0 
        pathlist_len = len(filepath)
        idx_block_map = {} # dict{block_index: block}
        path_idx_map = {} # dict{path: list(block_index)}
        for m, p in enumerate(filepath):
            with open(p, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # ---改行コード×delim_threasでsplitする処理。
            delimcount = 0  # \nが出てきた回数
            next_start_idx = 0  # 次回の開始インデックス
            for n, line in enumerate(lines):
                if line == delimiter:
                    delimcount += 1
                    if delimcount == delim_threas:  # \nがsplit回数出たらstr抽出、カウンタ類をリセット、更新
                        idx_block_map[block_count] = lines[next_start_idx : n - delim_threas + 1]
                        next_start_idx = n + 1
                        delimcount = 0
                        block_count += 1
                else:
                    delimcount = 0

                # ---最後のファイルかつ最終ブロックの場合。残りを全て入れる
                if n == (len(lines)-1):
                    idx_block_map[block_count] = lines[next_start_idx :]
                    block_count += 1
            
            path_idx_map[p] = [i for i in range(next_start_map_count, block_count+1)]
            next_start_map_count = block_count + 1

        return idx_block_map, path_idx_map


    def search2(self, query, get_find_indexces=False):
        _query = query.lower() # 小文字変換
        retdic = {}

        for n, datas in self.db_small.items(): # 小文字データベースから検索
            hit_line_idx = []
            for m, lines in enumerate(datas): # データのlines取得
                if _query in lines: # 検索対象が見つかればリストに追加
                    hit_line_idx.append(m)
            if len(hit_line_idx) > 0:
                retdic[n] = hit_line_idx

        return retdic

    @property
    def db(self):
        return self.__db


if __name__ == "__main__":
    db = Textdb(debugfilepaths)
    a = db.search2("git")
    print(a)
