import aiobungie
from pydantic import BaseModel
from destiny.manifest import Manifest


class ItemObjectives:
    hash: int
    progress: int
    name: str


class ObjectiveInfo(BaseModel):
    uiLabel: str
    progress: int | None


class DisplayProperties(BaseModel):
    name: str
    objectives: list[ObjectiveInfo] = []


class DestinyItemProperties(BaseModel):
    displayProperties: DisplayProperties
    hash: int
    instanceId: int | None


async def get_inventory_data(client: aiobungie.client.Client, manifest_client: Manifest, membership_id: int,
                             character_id: int) -> list[DestinyItemProperties]:
    item_info: list[DestinyItemProperties] = []

    async with client.rest:
        inventory_data = await client.fetch_character(member_id=membership_id,
                                                      membership_type=aiobungie.MembershipType.STEAM,
                                                      character_id=character_id,
                                                      components=[aiobungie.ComponentType.CHARACTER_INVENTORY,
                                                                  aiobungie.ComponentType.CHARACTER_EQUIPMENT,
                                                                  aiobungie.ComponentType.ITEM_PLUG_OBJECTIVES])

    if inventory_data.inventory is not None:  # in case inventory is private
        for item in inventory_data.inventory:
            item_data = await manifest_client.get_item_json(table="DestinyInventoryItemDefinition", item_hash=item.hash)
            item_properties: DestinyItemProperties = DestinyItemProperties.parse_obj(item_data)
            item_properties.instanceId = item.instance_id
            item_info.append(item_properties)

    for item in inventory_data.equipment:
        item_data = await manifest_client.get_item_json(table="DestinyInventoryItemDefinition", item_hash=item.hash)
        item_properties: DestinyItemProperties = DestinyItemProperties.parse_obj(item_data)
        item_properties.instanceId = item.instance_id
        item_info.append(item_properties)

    for instance_id, objective_dict in inventory_data.item_components.plug_objectives.items():
        for objective_list in objective_dict.values():
            for objective in objective_list:
                objective_manifest = await manifest_client.get_item_json(table="DestinyObjectiveDefinition",
                                                                   item_hash=objective.hash)
                objective_info: ObjectiveInfo = ObjectiveInfo.parse_obj(objective_manifest)
                objective_info.progress = objective.progress
                for item in item_info:
                    if item.instanceId == instance_id:
                        item.displayProperties.objectives.append(objective_info)
    return item_info
