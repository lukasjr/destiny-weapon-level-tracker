import json
import aiobungie
import sqlite3
from pathlib import Path


class Manifest:
    def __init__(self, file_name: str):
        self.client = aiobungie.RESTClient("")
        self.file_name = file_name
        self.cur = None

    async def get_item_json(self, table: str, item_hash: int) -> dict | None:
        if self.cur is None:
            self.cur = sqlite3.connect(self.file_name)
        # the hash value is uint. Convert to signed int.
        converted_hash = int(item_hash) if int(item_hash) < (2 ** 32 / 2 - 1) else int(item_hash) - (2 ** 32)
        json_data = self.cur.execute(
            "select json from {} where id = {}".format(table, converted_hash)
        ).fetchone()
        if json_data is None:
            return None
        return json.loads(json_data[0])

    async def downloaded_manifest_version(self) -> str:
        async with self.client:
            return await self.client.fetch_manifest_version()

    async def download_manifest(self) -> None:
        current_version = await self.downloaded_manifest_version()
        with open("manifest.version", "r") as f:
            downloaded_version = f.readline()
        if Path(self.file_name).is_file() and downloaded_version == current_version:
            return
        else:
            print("Downloading manifest...")
            async with self.client:
                await self.client.download_manifest(force=True)
            if downloaded_version != current_version:
                with open("manifest.version", "w") as f:
                    f.write(current_version)
