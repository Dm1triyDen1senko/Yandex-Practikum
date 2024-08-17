from pathlib import Path
import csv
from datetime import datetime as dt
from collections import Counter

from scrapy.exceptions import DropItem

BASE_DIR = Path(__file__).parent.parent

RESULTS_DIR = 'results'


class PepParsePipeline:
    def open_spider(self, spider):
        self.counter = Counter()

        self.time = dt.now().strftime('%Y-%m-%d_%H-%M-%S')

    def process_item(self, item, spider):
        self.counter[item['status']] += 1

        if 'status' not in item:
            raise DropItem('Такого статуса нет!')

        return item

    def close_spider(self, spider):
        results_dir = BASE_DIR / RESULTS_DIR
        file_path = results_dir / f'status_summary_{self.time}.csv'
        file = csv.writer(open(file_path, 'w'))
        file.writerow(['Статус', 'Количество'])
        self.counter['Total'] = sum(self.counter.values())
        file.writerows(self.counter.items())
