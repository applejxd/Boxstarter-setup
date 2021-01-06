# cf. https://keypirinha.com/api/plugin.html
import keypirinha as kp
import keypirinha_util as kpu

from collections import namedtuple
import datetime
import os
import subprocess


class Ghq(kp.Plugin):
    ITEMCAT_RESULT = kp.ItemCategory.USER_BASE + 1

    # 処理結果を保存するリスト
    ghq_root = ""
    repos = []

    def __init__(self):
        super().__init__()

    def on_start(self):
        """初期化"""
        self.ghq_root = subprocess.run(
            'powershell -ExecutionPolicy Bypass ghq root',
            shell=True, stdout=subprocess.PIPE, check=True
        ).stdout.decode('utf-8')
        self.repos = []
        # ItemCategory に CatalogAction のリストを割り当て
        self.set_actions(self.ITEMCAT_RESULT, [
            # CatalogAction オブジェクトの生成
            self.create_action(
                name="copy",
                label="Copy",
                short_desc="Copy the name of the answer")
        ])

    def on_catalog(self):
        """
        カタログ生成.
        Keypirinha で起動するためのトリガー・説明など.
        """
        # CatalogItem のリストで catalog の変更
        self.set_catalog([
            # CatalogItem 生成
            self.create_item(
                # 入力のカテゴリ
                category=kp.ItemCategory.KEYWORD,
                # 表示名
                label="ghq",
                # 説明
                short_desc="Open project cloned by ghq",
                # 起動キーワード
                target="ghq",
                # 引数を要求する
                args_hint=kp.ItemArgsHint.REQUIRED,
                # 重複なしで履歴を保存
                hit_hint=kp.ItemHitHint.NOARGS)
        ])

    def on_activated(self):
        """
        ランチャー表示時の処理.
        ghq のリスト取得
        """
        # バイナリ文字列を変換・改行コードでリスト化
        self.repos = subprocess.run(
            'powershell -ExecutionPolicy Bypass ghq list',
            shell=True, stdout=subprocess.PIPE, check=True
        ).stdout.decode('utf-8').split()

    def on_suggest(self, user_input, items_chain):
        """検索処理

        Args:
            user_input : 入力内容
            items_chain : 選択したアイテム
        """
        # カテゴリが異なる場合
        if not items_chain or items_chain[-1].category() != kp.ItemCategory.KEYWORD:
            return

        # # 入力内容がない場合
        # if not user_input:
        #     self.history = []

        # 結果を履歴に追加
        # self.history.append(AnswerTuple(
        #     os.urandom(1)[0] % 2,
        #     datetime.datetime.now()))

        # サジェスト作成
        suggestions = []
        # 降順ループ
        for idx in range(0, len(self.repos)):
            # サジェスト追加
            suggestions.append(
                # CatalogItem オブジェクト生成
                self.create_item(
                    category=self.ITEMCAT_RESULT,
                    label=self.repos[idx],
                    short_desc=self.repos[idx],
                    target=self.repos[idx],
                    args_hint=kp.ItemArgsHint.FORBIDDEN,
                    hit_hint=kp.ItemHitHint.IGNORE)
            )

        # サジェスト表示
        self.set_suggestions(
            suggestions,
            # マッチング方式
            kp.Match.FUZZY,
            # ソートのルール
            kp.Sort.NONE
        )

    def on_execute(self, item, action):
        """実行処理

        Args:
            item : CatalogItem
            action : 
        """
        if item and item.category() == self.ITEMCAT_RESULT:
            command = 'code ' + self.ghq_root + "/" + item.target()
            subprocess.run(command, shell=True, check=True)
