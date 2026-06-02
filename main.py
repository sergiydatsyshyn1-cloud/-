from abc import ABC, abstractmethod
import json

# ==========================================
# 1. ООП СТРУКТУРА (Класи вправ та тренування)
# ==========================================

class Exercise(ABC):
    """Абстрактний клас базової вправи"""
    def __init__(self, name: str, duration_min: int):
        self.name = name
        self.duration_min = duration_min

    @abstractmethod
    def calories_burned(self) -> float:
        pass


class CardioExercise(Exercise):
    """Клас для кардіо-вправ"""
    def __init__(self, name: str, duration_min: int, intensity: float):
        super().__init__(name, duration_min)
        # Обмежуємо інтенсивність у межах 1.0–2.0 для безпеки розрахунків
        self.intensity = max(1.0, min(2.0, intensity))

    def calories_burned(self) -> float:
        # Формула: duration_min * 8 * intensity
        return float(self.duration_min * 8 * self.intensity)


class StrengthExercise(Exercise):
    """Клас для силових вправ"""
    def __init__(self, name: str, duration_min: int, weight_kg: float):
        super().__init__(name, duration_min)
        self.weight_kg = weight_kg

    def calories_burned(self) -> float:
        # Формула: duration_min * 5 + weight_kg * 0.5
        return float(self.duration_min * 5 + self.weight_kg * 0.5)


class Workout:
    """Клас для обліку всього тренування (Інкапсуляція та Поліморфізм)"""
    def __init__(self):
        self.__exercises = []  # Приватний список вправ

    def add(self, exercise: Exercise):
        if isinstance(exercise, Exercise):
            self.__exercises.append(exercise)
        else:
            raise TypeError("Можна додавати лише об'єкти, що наслідують Exercise")

    def total_calories(self) -> float:
        # Поліморфізм: викликаємо calories_burned() не знаючи точного типу вправи
        return sum(exe.calories_burned() for exe in self.__exercises)

    def summary(self) -> dict:
        exercises_data = []
        for exe in self.__exercises:
            info = {
                "name": exe.name,
                "duration_min": exe.duration_min,
                "calories": exe.calories_burned()
            }
            if isinstance(exe, CardioExercise):
                info["type"] = "cardio"
                info["intensity"] = exe.intensity
            elif isinstance(exe, StrengthExercise):
                info["type"] = "strength"
                info["weight_kg"] = exe.weight_kg
            exercises_data.append(info)

        return {
            "exercises": exercises_data,
            "total_calories": self.total_calories()
        }


# ==========================================
# 2. ІНСТРУМЕНТ (TOOL) ДЛЯ AI-АГЕНТА
# ==========================================

def calculate_workout(exercises: list) -> dict:
    """
    Приймає список словників з полями: type, name, duration_min 
    та intensity / weight_kg. Повертає звіт summary().
    """
    workout = Workout()
    
    for exe_data in exercises:
        exe_type = exe_data.get("type", "").lower()
        name = exe_data.get("name", "Невідома вправа")
        duration = int(exe_data.get("duration_min", 0))
        
        if exe_type == "cardio":
            intensity = float(exe_data.get("intensity", 1.0))
            exercise = CardioExercise(name, duration, intensity)
            workout.add(exercise)
            
        elif exe_type == "strength":
            weight = float(exe_data.get("weight_kg", 0.0))
            exercise = StrengthExercise(name, duration, weight)
            workout.add(exercise)
            
    return workout.summary()


# ==========================================
# 3. МОДЕЛЮВАННЯ РОБОТИ AI-АГЕНТА (Промпт + 3 Тести)
# ==========================================

class FitnessAgent:
    """Симуляція ШІ-агента фітнес-тренера"""
    def __init__(self):
        self.system_prompt = (
            "Ви — персональний фітнес-тренер. Ви розраховуєте калорії для тренувань "
            "та даєте рекомендації щодо навантаження за допомогою інструменту розрахунку. "
            "Відповідайте виключно українською мовою."
        )

    def handle_user_request(self, user_message: str, structured_data: list):
        print(f"👤 Користувач: {user_message}")
        
        # Агент викликає інструмент (Tool Use)
        tool_result = calculate_workout(structured_data)
        
        # Симуляція текстової відповіді агента на основі отриманих від інструменту даних
        total_cal = tool_result['total_calories']
        
        response = (
            f"🤖 Фітнес-Тренер: Чудове тренування! Я підрахував ваші енерговитрати. "
            f"Загалом ви спалили **{total_cal:.1f} ккал**.\nРекомендація: "
        )
        
        if total_cal < 250:
            response += "Це була хороша легка розминка / відновлювальне тренування. Не забувайте пити воду!"
        elif 250 <= total_cal <= 500:
            response += "Продуктивне тренування середньої інтенсивності. Оптимальний баланс для підтримки форми."
        else:
            response += "Потужна робота! Високе навантаження. Обов'язково зробіть якісну розтяжку та відпочиньте."
            
        print(response)
        print(f"📊 [Повні дані інструменту]: {json.dumps(tool_result, ensure_ascii=False, indent=2)}\n" + "-"*50)


# Створюємо агента
agent = FitnessAgent()

# --- Демонстрація: 3 запити з різними наборами вправ ---

# Запит 1: Легке кардіо
prompt_1 = "Я побігав зранку на доріжці в легкому темпі 20 хвилин."
data_1 = [{"type": "cardio", "name": "Біг на доріжці", "duration_min": 20, "intensity": 1.2}]
agent.handle_user_request(prompt_1, data_1)

# Запит 2: Силове тренування
prompt_2 = "Сьогодні був день ніг: робив присідання зі штангою 30 хвилин та випади 15 хвилин."
data_2 = [
    {"type": "strength", "name": "Присідання зі штангою", "duration_min": 30, "weight_kg": 60.0},
    {"type": "strength", "name": "Випади з гантелями", "duration_min": 15, "weight_kg": 20.0}
]
agent.handle_user_request(prompt_2, data_2)

# Запит 3: Змішане (Кросфіт / Інтенсивне)
prompt_3 = "Провів жорстке кругове тренування: 15 хвилин скакалки на максимум і 20 хвилин жиму лежачи."
data_3 = [
    {"type": "cardio", "name": "Скакалка", "duration_min": 15, "intensity": 1.9},
    {"type": "strength", "name": "Жим лежачи", "duration_min": 20, "weight_kg": 70.0}
]
agent.handle_user_request(prompt_3, data_3)
