import asyncio
import math
import sys
import time
import os
import aiobungie

from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TaskID
from destiny.manifest import Manifest
from destiny.inventory import get_inventory_data
from destiny.config import load_config


async def main() -> None:
    config = load_config("config.toml")

    bungie_client = aiobungie.Client(config.bungie.token)
    manifest_client = Manifest(file_name="manifest.sqlite3")
    await manifest_client.download_manifest()
    os.system('cls' if os.name == 'nt' else 'clear')
    item_info = await get_inventory_data(bungie_client, manifest_client, config.destiny.member_id,
                                         config.destiny.character_id)
    progress = Progress(
        TextColumn("[progress.description]{task.description}", style="bold"),
        BarColumn(complete_style="blue"),
        TaskProgressColumn("{task.percentage:>3.0f}%", markup=False, style="yellow")
    )

    tasks: dict[str, TaskID] = {}

    for item in item_info:
        weapon_level = 0
        weapon_progress = 0
        for objective in item.displayProperties.objectives:
            if objective.uiLabel == "crafting_weapon_level_progress":
                weapon_progress = objective.progress
            if objective.uiLabel == "crafting_weapon_level":
                weapon_level = objective.progress
        if weapon_level:
            tasks[item.displayProperties.name] = progress.add_task(
                f'{item.displayProperties.name:<15}{weapon_level:03}',
                total=100, completed=math.ceil(weapon_progress / 10))
    with progress:
        while True:
            time.sleep(10)
            item_info = await get_inventory_data(bungie_client, manifest_client, config.destiny.member_id,
                                                 config.destiny.character_id)
            for item in item_info:
                weapon_level = 0
                weapon_progress = 0
                for objective in item.displayProperties.objectives:
                    if objective.uiLabel == "crafting_weapon_level_progress":
                        weapon_progress = objective.progress
                    if objective.uiLabel == "crafting_weapon_level":
                        weapon_level = objective.progress
                if weapon_level:
                    progress.update(tasks[item.displayProperties.name], completed=weapon_progress / 10)


if __name__ == '__main__':

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit()
