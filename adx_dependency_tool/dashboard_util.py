import json
from model.function import Function
from model.table import Table
from model.page import Page
from model.query import Query
from model.tile import Tile
from pyspark.sql import SparkSession


class DashboardUtil():
    def __init__(self, dashboard_json_path, function_csv_path, table_csv_path):
        self.dashboard_json_path = dashboard_json_path
        self.function_csv_path = function_csv_path
        self.table_csv_path = table_csv_path
        self.spark = SparkSession.builder.getOrCreate()
        self._read_dashboard_json()
        self._read_function_csv()
        self._read_table_csv()

    def _read_dashboard_json(self):
        with open(self.dashboard_json_path) as f:
            self.dashboard_data = json.load(f)

    def _read_function_csv(self):
        self.functions_df = self.spark.read.option("escape", "\"").option(
            "multiLine", True).csv(self.function_csv_path, header=True).collect()
        self.function_names = [f['Name'] for f in self.functions_df]

    def _read_table_csv(self):
        self.tables_df = self.spark.read.option("escape", "\"").option(
            "multiLine", True).csv(self.table_csv_path, header=True).collect()
        self.table_names = [t['TableName'] for t in self.tables_df]

    def get_dashboard(self):
        return self.dashboard_data

    def get_pages(self):
        pages = []
        for p in self.dashboard_data['pages']:
            page = Page(p['id'], p['name'])
            pages.append(page)
        return pages

    def get_tiles(self):
        tiles = []
        for t in self.dashboard_data['tiles']:
            tile_id = t['id']
            title = t['title']
            page_id = t['pageId']
            pos = (t['layout']['x'], t['layout']['y'])
            if 'queryRef' in t:
                linked_query_id = t['queryRef']['queryId']
                tile = Tile(tile_id, linked_query_id, page_id, title, pos)
            else:
                tile = Tile(tile_id, None, page_id, title, pos)
            tiles.append(tile)
        return tiles

    def get_queries(self):
        queries = []
        for q in self.dashboard_data['queries']:
            query_id = q['id']
            content = q['text']
            query = Query(query_id, content,
                          self.function_names, self.table_names)
            queries.append(query)
        return queries

    def get_functions(self):
        functions = []
        for f in self.functions_df:
            name = f['Name']
            body = f['Body']
            folder = f['Folder']
            f = Function(name, body, folder,
                         self.function_names, self.table_names)
            functions.append(f)
        return functions

    def get_tables(self):
        tables = []
        for t in self.tables_df:
            name = t['TableName']
            db_name = t['DatabaseName']
            folder = t['Folder']
            t = Table(name, db_name, folder)
            tables.append(t)
        return tables
