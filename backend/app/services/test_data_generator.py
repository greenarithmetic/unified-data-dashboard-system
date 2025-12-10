"""Test data generator for development and testing"""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from faker import Faker

fake = Faker('ru_RU')


class TestDataGenerator:
    """Generate test data for development"""
    
    @staticmethod
    def generate_community_requests(count: int = 100) -> List[Dict[str, Any]]:
        """Generate test community requests"""
        themes = [
            "Дороги и тротуары",
            "Освещение улиц",
            "Вывоз мусора",
            "Общественный транспорт",
            "Парки и скверы",
            "Детские площадки",
            "Водоснабжение",
            "Отопление",
            "Электричество",
            "Шум от строительства",
            "Бездомные животные",
            "Торговля в неположенных местах",
            "Наркоторговля",
            "Пьяные граждане",
            "Поврежденные фасады",
            "Незаконная парковка",
            "Рекламные конструкции",
            "Канализация",
            "Ливневые стоки",
            "Озеленение"
        ]
        
        addresses = [
            "ул. Ленина, 15",
            "пр. Мира, 42",
            "ул. Советская, 7",
            "ул. Пушкина, 23",
            "ул. Гагарина, 56",
            "ул. Кирова, 12",
            "ул. Садовая, 34",
            "ул. Лесная, 89",
            "ул. Школьная, 45",
            "ул. Заводская, 67",
            "ул. Новая, 21",
            "ул. Центральная, 78",
            "ул. Молодежная, 33",
            "ул. Строителей, 90",
            "ул. Победы, 11"
        ]
        
        records = []
        start_date = datetime.now() - timedelta(days=30)
        
        for i in range(count):
            # Generate random date within last 30 days
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            
            record_date = start_date + timedelta(
                days=days_ago,
                hours=hours_ago,
                minutes=minutes_ago
            )
            
            theme = random.choice(themes)
            author = fake.name()
            
            # Generate realistic text based on theme
            text_templates = {
                "Дороги и тротуары": [
                    f"На {random.choice(addresses)} огромная яма на дороге, машины повреждают подвеску",
                    f"Тротуар на {random.choice(addresses)} разбит, невозможно пройти с коляской",
                    f"На перекрестке {random.choice(addresses)} нет разметки, постоянные аварии"
                ],
                "Освещение улиц": [
                    f"На {random.choice(addresses)} не работает фонарь уже неделю, темно и опасно",
                    f"Уличное освещение на {random.choice(addresses)} слишком тусклое",
                    f"Фонари на {random.choice(addresses)} мигают, нужен ремонт"
                ],
                "Вывоз мусора": [
                    f"Контейнеры на {random.choice(addresses)} переполнены, мусор валяется вокруг",
                    f"Мусор не вывозят уже 5 дней на {random.choice(addresses)}",
                    f"На {random.choice(addresses)} сломаны мусорные контейнеры"
                ],
                "Общественный транспорт": [
                    f"Автобус №{random.randint(1, 100)} постоянно опаздывает на остановке {random.choice(addresses)}",
                    f"На остановке {random.choice(addresses)} нет расписания",
                    f"В автобусе №{random.randint(1, 100)} грязно и воняет"
                ]
            }
            
            # Default text if no template for theme
            if theme in text_templates:
                text = random.choice(text_templates[theme])
            else:
                text = f"Проблема с {theme.lower()} на {random.choice(addresses)}. {fake.text(max_nb_chars=100)}"
            
            # Add some spam records (10% chance)
            is_spam = random.random() < 0.1
            if is_spam:
                spam_texts = [
                    "КУПЛЮ КВАРТИРУ СРОЧНО 89161234567",
                    "РЕКЛАМА: Скидки 50% в магазине на углу",
                    "ТЕСТОВОЕ СООБЩЕНИЕ для проверки системы",
                    "ПРОДАМ МАШИНУ НЕДОРОГО 89169876543",
                    "НАЙДЕН КОШЕЛЕК НА УЛИЦЕ ЛЕНИНА",
                    "МЕНЯЮ КВАРТИРУ НА ДАЧУ 89167778899"
                ]
                text = random.choice(spam_texts)
                author = "Спам-бот" if random.random() < 0.5 else fake.name()
            
            record = {
                "тема": theme,
                "дата": record_date.isoformat(),
                "от_кого": author,
                "текст": text,
                "адрес": random.choice(addresses) if random.random() < 0.8 else None,
                "ответ": random.random() < 0.6,  # 60% have response
                "source_id": f"test_{i}_{int(record_date.timestamp())}",
                "_row_number": i + 2
            }
            
            records.append(record)
        
        return records
    
    @staticmethod
    def generate_second_table_data(count: int = 50) -> List[Dict[str, Any]]:
        """Generate test data for second table"""
        records = []
        start_date = datetime.now() - timedelta(days=60)
        
        for i in range(count):
            days_ago = random.randint(0, 60)
            record_date = start_date + timedelta(days=days_ago)
            
            record = {
                "column1": f"Запись {i+1}",
                "column2": record_date.isoformat(),
                "column3": random.randint(100, 10000),
                "source_id": f"second_test_{i}_{int(record_date.timestamp())}",
                "_row_number": i + 2
            }
            
            records.append(record)
        
        return records


def generate_test_data_for_dataset(dataset_id: str, count: int = 100) -> List[Dict[str, Any]]:
    """Generate test data for specific dataset"""
    generator = TestDataGenerator()
    
    if dataset_id == "community_requests":
        return generator.generate_community_requests(count)
    elif dataset_id == "second_table":
        return generator.generate_second_table_data(count)
    else:
        # Generic test data for unknown datasets
        return [
            {
                "field1": f"Значение {i}",
                "field2": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                "field3": random.randint(1, 100),
                "source_id": f"generic_{i}_{int(datetime.now().timestamp())}",
                "_row_number": i + 2
            }
            for i in range(count)
        ]