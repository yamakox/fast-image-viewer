from django.core.management.base import BaseCommand
import api.dataset


class Command(BaseCommand):
    help = 'データセットフォルダー内の画像をスキャンします。'

    def handle(self, *args, **options):
        api.dataset.scan_dataset()
        self.stdout.write(
            self.style.SUCCESS('データセットフォルダーのスキャンが完了しました。\nエラーはログを参照してください。')
        )
