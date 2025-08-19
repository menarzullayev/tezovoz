# NEW-111
from typing import Any, Dict
from aiogram.fsm.context import FSMContext

class FSMDataManager:
    """
    FSMContext obyektini boshqarish uchun yordamchi sinf.
    """

    def __init__(self, state_context: FSMContext):
        self.state = state_context

    async def get_all_data(self) -> Dict[str, Any]:
        """Barcha saqlangan ma'lumotlarni qaytaradi."""
        return await self.state.get_data()

    async def set_field(self, key: str, value: Any) -> None:
        """Ma'lumotlar lug'atidagi bitta maydonni yangilaydi."""
        await self.state.update_data({key: value})

    async def get_field(self, key: str, default: Any = None) -> Any:
        """Ma'lumotlar lug'atidan bitta maydon qiymatini qaytaradi."""
        data = await self.state.get_data()
        return data.get(key, default)

    async def clear_all_data(self) -> None:
        """Barcha saqlangan ma'lumotlarni o'chiradi."""
        await self.state.clear()