from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession # Changed import
from sqlalchemy import select # Added import

from models import Division
from models.division import DivisionTypeEnum # Added import
from schemas import DivisionCreate, DivisionUpdate
from services.base import ServiceBase # Assuming ServiceBase can handle async or is not used by new method


class DivisionService(ServiceBase[Division, DivisionCreate, DivisionUpdate]):

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Division]: # Made async
        result = await db.execute(select(Division).filter(Division.name == name)) # Changed to async query
        return result.scalars().first()

    # Количество сотрудников по штату всего департамента
    # def get_count_emp_by_state(self): # Commented out as it's a placeholder and not async
    #     return 136

    async def get_divisions_for_user(
        self,
        db: AsyncSession,
        user_role: int,
        user_assigned_division_id: Optional[int],
        skip: int = 0,
        limit: int = 100
    ) -> List[Division]:
        if user_role == 1 or user_role == 4: # Superuser or System Admin
            result = await db.execute(select(Division).offset(skip).limit(limit))
            return list(result.scalars().all()) # Ensure list conversion

        elif user_role == 2 or user_role == 3: # Department Head or Management Head
            if user_assigned_division_id is None:
                return []

            user_division = await db.get(Division, user_assigned_division_id)
            if not user_division:
                return []

            # Traverse upwards to find the department node
            current_node = user_division
            department_node: Optional[Division] = None
            # Max depth to prevent infinite loops in case of misconfigured data
            max_depth_search = 10
            count = 0
            while current_node and count < max_depth_search:
                if current_node.division_type == DivisionTypeEnum.DEPARTMENT:
                    department_node = current_node
                    break
                if current_node.parent_division_id is None: # Reached top without finding department
                    # This might mean the user is in a structure not under a department (e.g. company level)
                    # Depending on policy, could return just their division, or all under their high-level division.
                    # For now, if their own division is a department, that's found. Otherwise, this path is taken.
                    # If user_division itself is the department, this loop isn't entered if first check is for current_node.
                    if user_division.division_type == DivisionTypeEnum.DEPARTMENT: # Check if user's own division is dept
                        department_node = user_division
                    break

                parent_division_obj = await db.get(Division, current_node.parent_division_id)
                current_node = parent_division_obj
                count +=1

            if not department_node: # No department ancestor found
                 # If user is in a high-level structure (e.g. Company directly), what to return?
                 # For now, if their assigned division is what they manage, and it's not a dept,
                 # let's assume they see their assigned division and its children as per original logic for roles 2/3.
                 # This means the "department node" effectively becomes their assigned division.
                 department_node = user_division # Treat user's own division as the "root" for listing

            # Fetch the department node itself and all its descendants
            divisions_to_return: List[Division] = []
            if department_node: # Ensure department_node is not None
                divisions_to_return.append(department_node)

                # Iteratively fetch children
                # This is a breadth-first traversal to get all descendants
                current_parent_ids = [department_node.id]

                processed_child_ids = {department_node.id} # To avoid re-processing if circular or deep

                while current_parent_ids:
                    children_results = await db.execute(
                        select(Division).where(Division.parent_division_id.in_(current_parent_ids))
                    )
                    children = list(children_results.scalars().all())

                    if not children:
                        break

                    new_children_ids = []
                    for child in children:
                        if child.id not in processed_child_ids:
                            divisions_to_return.append(child)
                            new_children_ids.append(child.id)
                            processed_child_ids.add(child.id)

                    current_parent_ids = new_children_ids
                    if not current_parent_ids: # No new children found to explore further
                        break

            # Apply pagination to the final list of divisions
            # Note: This simple slicing is not efficient for large datasets if done in Python.
            # For very large hierarchies, consider more complex pagination queries or limits at each level.
            paginated_divisions = divisions_to_return[skip : skip + limit]
            return paginated_divisions

        return [] # Default empty list for unknown roles or other cases


division_service = DivisionService(Division)
