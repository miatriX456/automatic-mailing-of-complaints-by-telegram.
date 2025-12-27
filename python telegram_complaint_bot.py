import requests
import random
import string
import os
import time
from datetime import datetime
from colorama import Fore, Style, init
import socket
import sys
import re

init(autoreset=True)


class FixedTelegramComplaintBot:
    def __init__(self):
        # Создаем папку для логов
        self.log_dir = "telegram_complaint_logs"
        os.makedirs(self.log_dir, exist_ok=True)

        # Файл лога
        self.log_file = os.path.join(self.log_dir, f"complaints_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

        self.log_event("INFO", "Инициализация бота...")

        self.session = requests.Session()
        self.setup_session()

        self.stats = {
            'total_sent': 0,
            'successful': 0,
            'failed': 0,
            'start_time': datetime.now()
        }

        # Загружаем шаблоны
        self.complaint_templates = self.load_complaint_templates()

        # Язык по умолчанию
        self.force_language = "random"

        self.log_event("INFO", "Бот инициализирован")

    def log_event(self, level, message):
        """Запись событий в лог"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)

            # Цветной вывод в консоль
            if level == "ERROR":
                print(Fore.RED + f"[{timestamp}] {message}" + Style.RESET_ALL)
            elif level == "WARNING":
                print(Fore.YELLOW + f"[{timestamp}] {message}" + Style.RESET_ALL)
            elif level == "SUCCESS":
                print(Fore.GREEN + f"[{timestamp}] {message}" + Style.RESET_ALL)
            else:
                print(Fore.CYAN + f"[{timestamp}] {message}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Ошибка записи в лог: {e}" + Style.RESET_ALL)

    def setup_session(self):
        """Настройка HTTP сессии"""
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry

        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            respect_retry_after_header=True
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        # Базовые заголовки
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })

    def load_complaint_templates(self):
        """Загрузка шаблонов с правильным разделением по языкам"""
        return {
            "Детская безопасность": {
                "ru": [
                    "Пользователь @{username} (ID: {user_id}) распространяет материалы, опасные для несовершеннолетних. Обнаружено нарушение политики защиты детей. Ссылка: {violation_link}",
                    "СРОЧНО: Угроза детской безопасности. Аккаунт {user_id} делится неприемлемым контентом. Доказательства: {violation_link} Требуется блокировка.",
                    "Жалоба на нарушение детской безопасности. Пользователь {user_id} контактирует с несовершеннолетними ненадлежащим образом. Нарушение: {violation_link}",
                    "Пользователь @{username} размещает контент 18+ в публичных каналах без ограничений по возрасту. ID: {user_id}. Нарушение: {violation_link}",
                    "Пропаганда насилия среди подростков от пользователя {user_id}. Материалы содержат жестокость. Ссылка на доказательства: {violation_link}",
                    "Пользователь {user_id} ведет частные переписки с детьми с сексуальными намеками. Требуется срочное расследование. Контент: {violation_link}",
                    "Публикация детской порнографии через аккаунт @{username}. ID: {user_id}. Ссылки на доказательства: {violation_link}",
                    "Пользователь создает группы для несовершеннолетних с опасным контентом. ID: {user_id}. Группа: {violation_link}",
                    "Вербовка детей в опасные группы через Telegram. Пользователь {user_id} предлагает детям опасные материалы. Доказательства: {violation_link}",
                    "Торговля детьми через Telegram. Аккаунт {user_id} участвует в незаконной деятельности. Подробности: {violation_link}",
                    "Пользователь @{username} вымогает интимные фото у несовершеннолетних. ID: {user_id}. Переписка: {violation_link}",
                    "Распространение инструкций по суициду среди подростков от пользователя {user_id}. Контент: {violation_link}",
                    "Создание фейковых детских групп для мошенничества. Пользователь {user_id}. Группа: {violation_link}",
                    "Пользователь {user_id} публикует фото детей без согласия родителей с неприличными комментариями. Контент: {violation_link}",
                    "Пропаганда наркотиков среди несовершеннолетних через аккаунт @{username}. ID: {user_id}. Материалы: {violation_link}",
                    "Шантаж детей через Telegram. Пользователь {user_id} угрожает несовершеннолетним. Свидетельства: {violation_link}",
                    "Создание каналов с детской порнографией. Администратор {user_id}. Канал: {violation_link}",
                    "Пользователь {user_id} под видом ребенка втирается в доверие к подросткам. Доказательства обмана: {violation_link}",
                    "Распространение материалов для педофилов через Telegram. Аккаунт @{username} (ID: {user_id}). Контент: {violation_link}",
                    "Организация незаконных встреч с детьми через Telegram. Пользователь {user_id}. Переписка: {violation_link}",
                ],
                "en": [
                    "URGENT: Child safety violation. User @{username} (ID: {user_id}) shares inappropriate content. Evidence: {violation_link} Please investigate immediately.",
                    "Report of child endangerment. Account {user_id} creates unsafe conditions. Link: {violation_link} Requires immediate attention.",
                    "Complaint about content with minors. User @{username} violates child protection policies. Reference: {violation_link} Request account suspension.",
                    "User {user_id} distributes child pornography. Evidence: {violation_link} This is illegal content requiring immediate action.",
                    "Account @{username} (ID: {user_id}) grooms minors in private chats. Screenshots: {violation_link} Urgent intervention needed.",
                    "Child exploitation materials shared by user {user_id}. Links to evidence: {violation_link} This violates Telegram's ToS.",
                    "User creates channels targeting children with adult content. ID: {user_id}. Channel link: {violation_link}",
                    "Pedophile activity detected. User {user_id} shares illegal materials involving minors. Proof: {violation_link}",
                    "User @{username} blackmails children for explicit photos. ID: {user_id}. Chat evidence: {violation_link}",
                    "Suicide promotion targeting teenagers by user {user_id}. Content: {violation_link} This is extremely dangerous.",
                    "Child trafficking network operating via Telegram. User {user_id} is involved. Evidence: {violation_link}",
                    "Account {user_id} shares drug promotion content with minors. Materials: {violation_link} Violates multiple policies.",
                    "User pretends to be a child to gain trust of minors. ID: {user_id}. Proof of deception: {violation_link}",
                    "Distribution of CSAM (Child Sexual Abuse Material) by @{username}. ID: {user_id}. Evidence: {violation_link}",
                    "User organizes illegal meetings with minors. Account {user_id}. Chat logs: {violation_link}",
                    "Child predators using Telegram for illegal activities. User {user_id} is active. Evidence: {violation_link}",
                    "Sharing instructions for child abuse. User {user_id} violates laws. Content: {violation_link}",
                    "Exploiting children for financial gain through Telegram. Account {user_id}. Proof: {violation_link}",
                    "User @{username} uses Telegram to distribute child exploitation content. ID: {user_id}. Links: {violation_link}",
                    "Creating fake child profiles for illegal purposes. User {user_id}. Evidence: {violation_link}",
                ]
            },
            "Спам": {
                "ru": [
                    "Пользователь @{username} (ID: {user_id}) занимается массовой рассылкой спама. Отправляет нежелательные рекламные сообщения в чаты. Ссылка на спам: {violation_link}",
                    "Спам-активность от аккаунта {user_id}. Рассылает рекламу без согласия пользователей. Нарушение: {violation_link} Прошу принять меры.",
                    "Массовая рассылка рекламы криптовалютных мошенников. Пользователь {user_id} спамит в чатах. Пример: {violation_link}",
                    "Бот-спамер @{username} добавляет пользователей в группы без согласия. ID: {user_id}. Жалобы: {violation_link}",
                    "Пользователь {user_id} рассылает фишинг-ссылки под видом официальных сервисов. Спам: {violation_link}",
                    "Массовый спам с предложениями работы на дому (скам). Аккаунт {user_id}. Сообщения: {violation_link}",
                    "Спам-рассылка с порно-сайтами и казино от пользователя @{username}. ID: {user_id}. Контент: {violation_link}",
                    "Пользователь создает фейковые аккаунты для спама. Основной ID: {user_id}. Доказательства: {violation_link}",
                    "Спам в личные сообщения с угрозами блокировки аккаунта. Пользователь {user_id}. Пример: {violation_link}",
                    "Рассылка вирусных ссылок через Telegram. Пользователь @{username} (ID: {user_id}). Ссылки: {violation_link}",
                    "Спам комментариями под постами в каналах. Пользователь {user_id} оставляет сотни рекламных сообщений. Пример: {violation_link}",
                    "Автоматическая рассылка с помощью ботов. Пользователь {user_id} нарушает правила использования API. Доказательства: {violation_link}",
                    "Спам с предложениями взлома аккаунтов. Пользователь @{username} (ID: {user_id}). Сообщения: {violation_link}",
                    "Массовая рассылка фейковых новостей. Пользователь {user_id} распространяет дезинформацию. Пример: {violation_link}",
                    "Спам с поддельными конкурсами и розыгрышами. Аккаунт {user_id} обманывает пользователей. Доказательства: {violation_link}",
                    "Рассылка рекламы лекарств и БАДов без лицензии. Пользователь {user_id}. Сообщения: {violation_link}",
                    "Спам с финансовыми пирамидами и MLM. Пользователь @{username} (ID: {user_id}). Контент: {violation_link}",
                    "Массовая рассылка в группы с предложениями секс-услуг. Пользователь {user_id}. Нарушение: {violation_link}",
                    "Спам с поддельными услугами взлома Wi-Fi и соцсетей. Аккаунт {user_id}. Пример: {violation_link}",
                    "Рассылка фейковых уведомлений от администрации Telegram. Пользователь {user_id} имитирует официальные сообщения. Доказательства: {violation_link}",
                ],
                "en": [
                    "Spam report: User @{username} (ID: {user_id}) sends unsolicited advertisements. Evidence: {violation_link} Please take action against spam.",
                    "Mass spamming detected from account {user_id}. User violates anti-spam policy. Link to spam messages: {violation_link}",
                    "User {user_id} sends cryptocurrency scam spam to multiple groups. Evidence: {violation_link} This is financial spam.",
                    "Bot spam: Account @{username} adds users to groups without consent. ID: {user_id}. Complaints: {violation_link}",
                    "Phishing spam from user {user_id}. Fake links pretending to be official services. Examples: {violation_link}",
                    "Mass spam with work-from-home scams. Account {user_id} deceives users. Messages: {violation_link}",
                    "Spam with pornographic content and casino ads from user @{username}. ID: {user_id}. Content: {violation_link}",
                    "User creates multiple fake accounts for spamming. Main ID: {user_id}. Evidence: {violation_link}",
                    "Spam in private messages with account suspension threats. User {user_id}. Example: {violation_link}",
                    "Virus link distribution via Telegram spam. User @{username} (ID: {user_id}). Links: {violation_link}",
                    "Comment spam under channel posts. User {user_id} leaves hundreds of ads. Example: {violation_link}",
                    "Automated spam using bots. User {user_id} violates API terms. Evidence: {violation_link}",
                    "Spam with account hacking offers. User @{username} (ID: {user_id}). Messages: {violation_link}",
                    "Mass distribution of fake news spam. User {user_id} spreads misinformation. Example: {violation_link}",
                    "Spam with fake contests and giveaways. Account {user_id} scams users. Evidence: {violation_link}",
                    "Unlicensed medicine and supplement ads spam. User {user_id}. Messages: {violation_link}",
                    "Pyramid scheme and MLM spam. User @{username} (ID: {user_id}). Content: {violation_link}",
                    "Mass spam with sex service offers in groups. User {user_id}. Violation: {violation_link}",
                    "Spam with fake hacking services for Wi-Fi and social media. Account {user_id}. Example: {violation_link}",
                    "Fake Telegram admin notification spam. User {user_id} impersonates official accounts. Evidence: {violation_link}",
                ]
            },
            "Мошенничество": {
                "ru": [
                    "Мошенничество с криптовалютой от пользователя {user_id}. Обман при выводе средств. Доказательства: {violation_link}",
                    "Пользователь @{username} занимается финансовыми махинациями. ID: {user_id}. Нарушение: {violation_link}",
                    "Финансовый скам: пользователь {user_id} обещает высокий доход на крипто-инвестициях. Пример обмана: {violation_link}",
                    "Мошенник выманивает деньги под предлогом помощи в эмиграции. Пользователь @{username} (ID: {user_id}). Доказательства: {violation_link}",
                    "Продажа фейковых документов и паспортов. Пользователь {user_id} занимается подделкой. Контент: {violation_link}",
                    "Обман при продаже аккаунтов Telegram Premium. Пользователь {user_id} берет предоплату и блокирует. Доказательства: {violation_link}",
                    "Финансовая пирамида под видом инвестиционного клуба. Организатор {user_id}. Группа: {violation_link}",
                    "Мошенничество с арендой жилья. Пользователь @{username} берет задаток и исчезает. ID: {user_id}. Чат: {violation_link}",
                    "Продажа несуществующих товаров на маркетплейсе. Пользователь {user_id} обманывает покупателей. Доказательства: {violation_link}",
                    "Фейковые благотворительные сборы. Пользователь {user_id} использует фото больных детей для вымогательства. Контент: {violation_link}",
                    "Обман при обмене валют. Пользователь @{username} (ID: {user_id}) не возвращает деньги после перевода. Доказательства: {violation_link}",
                    "Мошенничество с кредитами и микрозаймами. Пользователь {user_id} берет комиссию и не выдает займ. Пример: {violation_link}",
                    "Скам с предоплатой за работу. Пользователь {user_id} набирает фрилансеров, берет тестовые задания и не платит. Доказательства: {violation_link}",
                    "Продажа фейковых курсов и обучений. Пользователь @{username} (ID: {user_id}) обещает золотые горы. Контент: {violation_link}",
                    "Мошенничество с гадалками и экстрасенсами. Пользователь {user_id} выманивает деньги на снятие порчи. Чат: {violation_link}",
                    "Финансовый обман под видом помощи украинским беженцам. Пользователь {user_id}. Доказательства: {violation_link}",
                    "Скам с покупкой б/у техники. Пользователь отправляет кирпичи вместо iPhone. ID: {user_id}. Переписка: {violation_link}",
                    "Мошенничество с онлайн-казино и ставками. Пользователь {user_id} управляет поддельными казино. Ссылки: {violation_link}",
                    "Вымогательство денег под угрозой слива переписки. Пользователь @{username} (ID: {user_id}). Доказательства: {violation_link}",
                    "Фейковые инвестиции в NFT и метавселенные. Пользователь {user_id} собирает деньги на несуществующие проекты. Контент: {violation_link}",
                ],
                "en": [
                    "Fraud report: User {user_id} runs cryptocurrency scam. Evidence: {violation_link}",
                    "Financial scam by account @{username}. User deceives people for money. Reference: {violation_link}",
                    "Crypto investment scam. User {user_id} promises unrealistic returns. Proof: {violation_link}",
                    "Scammer fakes emigration assistance services. User @{username} (ID: {user_id}). Evidence: {violation_link}",
                    "Fake document and passport sales. User {user_id} sells forged papers. Content: {violation_link}",
                    "Telegram Premium account sale scam. User {user_id} takes prepayment and blocks. Proof: {violation_link}",
                    "Pyramid scheme disguised as investment club. Organizer {user_id}. Group: {violation_link}",
                    "Rental fraud: User @{username} takes deposit and disappears. ID: {user_id}. Chat: {violation_link}",
                    "Sale of non-existent goods on marketplace. User {user_id} scams buyers. Evidence: {violation_link}",
                    "Fake charity fundraising. User {user_id} uses sick children photos for extortion. Content: {violation_link}",
                    "Currency exchange scam. User @{username} (ID: {user_id}) doesn't return money after transfer. Evidence: {violation_link}",
                    "Loan and microcredit fraud. User {user_id} takes commission but doesn't provide loan. Example: {violation_link}",
                    "Freelance prepayment scam. User {user_id} hires freelancers, gets work done, doesn't pay. Evidence: {violation_link}",
                    "Fake course and training sales. User @{username} (ID: {user_id}) promises unrealistic results. Content: {violation_link}",
                    "Fortune teller and psychic fraud. User {user_id} extorts money for 'removing curses'. Chat: {violation_link}",
                    "Financial scam disguised as aid to Ukrainian refugees. User {user_id}. Evidence: {violation_link}",
                    "Used electronics scam: User sends bricks instead of iPhone. ID: {user_id}. Correspondence: {violation_link}",
                    "Online casino and betting fraud. User {user_id} operates fake casinos. Links: {violation_link}",
                    "Blackmail for money with threat of leaking chats. User @{username} (ID: {user_id}). Evidence: {violation_link}",
                    "Fake NFT and metaverse investments. User {user_id} collects money for non-existent projects. Content: {violation_link}",
                ]
            },
            "Терроризм и экстремизм": {
                "ru": [
                    "Пропаганда терроризма. Пользователь {user_id} распространяет материалы ИГИЛ*. Контент: {violation_link}",
                    "Вербовка в террористические организации через Telegram. Пользователь @{username} (ID: {user_id}). Группа: {violation_link}",
                    "Распространение инструкций по изготовлению взрывчатки. Пользователь {user_id} нарушает антитеррористическое законодательство. Материалы: {violation_link}",
                    "Пропаганда насильственного свержения власти. Пользователь {user_id} призывает к террору. Сообщения: {violation_link}",
                    "Создание каналов для координации экстремистских действий. Администратор {user_id}. Канал: {violation_link}",
                    "Распространение идеологии нацизма и расизма. Пользователь @{username} (ID: {user_id}). Контент: {violation_link}",
                    "Призывы к этнической ненависти и геноциду. Пользователь {user_id} нарушает международное право. Доказательства: {violation_link}",
                    "Организация незаконных вооруженных формирований. Пользователь {user_id} вербует боевиков. Чат: {violation_link}",
                    "Пропаганда деятельности запрещенных организаций. Пользователь {user_id} распространяет материалы ХАМАС*. Контент: {violation_link}",
                    "Сбор средств на террористическую деятельность. Пользователь @{username} (ID: {user_id}). Доказательства: {violation_link}",
                    "Координация атак на гражданские объекты. Пользователь {user_id} планирует преступления. Переписка: {violation_link}",
                    "Распространение экстремистской литературы. Пользователь {user_id} делится книгами запрещенных авторов. Файлы: {violation_link}",
                    "Создание групп для подготовки террористов-одиночек. Пользователь {user_id}. Группа: {violation_link}",
                    "Пропаганда религиозного экстремизма. Пользователь {user_id} призывает к джихаду. Контент: {violation_link}",
                    "Распространение символики запрещенных организаций. Пользователь @{username} (ID: {user_id}). Изображения: {violation_link}",
                    "Вербовка женщин в ряды террористов. Пользователь {user_id} использует Telegram для пропаганды. Доказательства: {violation_link}",
                    "Координация деятельности ячеек запрещенной организации. Пользователь {user_id} является координатором. Чат: {violation_link}",
                    "Пропаганда насилия на почве национальной розни. Пользователь {user_id} разжигает межнациональную ненависть. Контент: {violation_link}",
                    "Распространение фейковых новостей для провокации беспорядков. Пользователь {user_id}. Материалы: {violation_link}",
                    "Организация несанкционированных митингов с призывами к насилию. Пользователь @{username} (ID: {user_id}). Планы: {violation_link}",
                ],
                "en": [
                    "Terrorism propaganda. User {user_id} spreads ISIS* materials. Content: {violation_link}",
                    "Recruitment for terrorist organizations via Telegram. User @{username} (ID: {user_id}). Group: {violation_link}",
                    "Distribution of explosive manufacturing instructions. User {user_id} violates anti-terror laws. Materials: {violation_link}",
                    "Propaganda of violent overthrow of government. User {user_id} calls for terror. Messages: {violation_link}",
                    "Channel creation for coordinating extremist activities. Admin {user_id}. Channel: {violation_link}",
                    "Spread of Nazi and racist ideology. User @{username} (ID: {user_id}). Content: {violation_link}",
                    "Calls for ethnic hatred and genocide. User {user_id} violates international law. Evidence: {violation_link}",
                    "Organization of illegal armed groups. User {user_id} recruits militants. Chat: {violation_link}",
                    "Propaganda of banned organizations' activities. User {user_id} spreads HAMAS* materials. Content: {violation_link}",
                    "Fundraising for terrorist activities. User @{username} (ID: {user_id}). Evidence: {violation_link}",
                    "Coordination of attacks on civilian targets. User {user_id} plans crimes. Correspondence: {violation_link}",
                    "Distribution of extremist literature. User {user_id} shares banned authors' books. Files: {violation_link}",
                    "Group creation for lone wolf terrorist training. User {user_id}. Group: {violation_link}",
                    "Religious extremism propaganda. User {user_id} calls for jihad. Content: {violation_link}",
                    "Spread of banned organizations' symbols. User @{username} (ID: {user_id}). Images: {violation_link}",
                    "Recruitment of women into terrorist ranks. User {user_id} uses Telegram for propaganda. Evidence: {violation_link}",
                    "Coordination of banned organization cells. User {user_id} is coordinator. Chat: {violation_link}",
                    "Propaganda of violence based on national strife. User {user_id} incites interethnic hatred. Content: {violation_link}",
                    "Spread of fake news to provoke riots. User {user_id}. Materials: {violation_link}",
                    "Organization of unauthorized rallies with calls for violence. User @{username} (ID: {user_id}). Plans: {violation_link}",
                ]
            },
            "Насилие и жестокость": {
                "ru": [
                    "Пропаганда насилия и жестокости. Пользователь {user_id} делится видео с пытками животных. Контент: {violation_link}",
                    "Распространение сцен реального насилия и убийств. Пользователь @{username} (ID: {user_id}). Видео: {violation_link}",
                    "Группы с материалами кибербуллинга и травли. Администратор {user_id}. Группа: {violation_link}",
                    "Призывы к физической расправе над политиками. Пользователь {user_id} угрожает убийством. Сообщения: {violation_link}",
                    "Распространение инструкций по нанесению телесных повреждений. Пользователь {user_id}. Материалы: {violation_link}",
                    "Публикация фото и видео с мест преступлений. Пользователь @{username} (ID: {user_id}) нарушает этические нормы. Контент: {violation_link}",
                    "Создание групп для координации избиений и расправ. Пользователь {user_id}. Чат: {violation_link}",
                    "Пропаганда домашнего насилия. Пользователь {user_id} делится советами как избивать женщин. Доказательства: {violation_link}",
                    "Распространение материалов с реальными самоубийствами. Пользователь {user_id} нарушает правила платформы. Видео: {violation_link}",
                    "Призывы к линчеванию и самосуду. Пользователь @{username} (ID: {user_id}). Сообщения: {violation_link}",
                    "Публикация контента с пытками военнопленных. Пользователь {user_id} нарушает международное право. Материалы: {violation_link}",
                    "Создание каналов с записями драк и избиений. Администратор {user_id}. Канал: {violation_link}",
                    "Распространение видео с реальными авариями и смертями. Пользователь {user_id} получает удовольствие от чужих страданий. Контент: {violation_link}",
                    "Пропаганда каннибализма и людоедства. Пользователь {user_id} делится запрещенными материалами. Доказательства: {violation_link}",
                    "Публикация инструкций по изготовлению оружия. Пользователь @{username} (ID: {user_id}). Файлы: {violation_link}",
                    "Создание групп для травли конкретных людей. Пользователь {user_id} организует кибербуллинг. Группа: {violation_link}",
                    "Распространение сцен сексуального насилия. Пользователь {user_id} делится материалами без согласия жертв. Контент: {violation_link}",
                    "Пропаганда эвтаназии и помощи в самоубийстве. Пользователь {user_id} нарушает законодательство. Сообщения: {violation_link}",
                    "Публикация фото и видео с жертвами катастроф без цензуры. Пользователь {user_id}. Материалы: {violation_link}",
                    "Создание контента с жестокими розыгрышами и пранками. Пользователь @{username} (ID: {user_id}) причиняет реальный вред людям. Видео: {violation_link}",
                ],
                "en": [
                    "Violence and cruelty propaganda. User {user_id} shares animal torture videos. Content: {violation_link}",
                    "Distribution of real violence and murder scenes. User @{username} (ID: {user_id}). Video: {violation_link}",
                    "Groups with cyberbullying and harassment materials. Admin {user_id}. Group: {violation_link}",
                    "Calls for physical violence against politicians. User {user_id} threatens murder. Messages: {violation_link}",
                    "Distribution of bodily harm instructions. User {user_id}. Materials: {violation_link}",
                    "Publication of crime scene photos and videos. User @{username} (ID: {user_id}) violates ethics. Content: {violation_link}",
                    "Group creation for coordinating beatings. User {user_id}. Chat: {violation_link}",
                    "Domestic violence propaganda. User {user_id} shares tips on beating women. Evidence: {violation_link}",
                    "Distribution of real suicide materials. User {user_id} violates platform rules. Video: {violation_link}",
                    "Calls for lynching and vigilante justice. User @{username} (ID: {user_id}). Messages: {violation_link}",
                    "Publication of prisoner torture content. User {user_id} violates international law. Materials: {violation_link}",
                    "Channel creation with fight and beating recordings. Admin {user_id}. Channel: {violation_link}",
                    "Distribution of real accident and death videos. User {user_id} enjoys others' suffering. Content: {violation_link}",
                    "Cannibalism and human eating propaganda. User {user_id} shares banned materials. Evidence: {violation_link}",
                    "Publication of weapon manufacturing instructions. User @{username} (ID: {user_id}). Files: {violation_link}",
                    "Group creation for targeting specific individuals. User {user_id} organizes cyberbullying. Group: {violation_link}",
                    "Distribution of sexual violence scenes. User {user_id} shares materials without victim consent. Content: {violation_link}",
                    "Euthanasia and suicide assistance propaganda. User {user_id} violates laws. Messages: {violation_link}",
                    "Publication of uncensored disaster victim photos/videos. User {user_id}. Materials: {violation_link}",
                    "Creation of cruel pranks causing real harm. User @{username} (ID: {user_id}) hurts people. Video: {violation_link}",
                ]
            },
            "Наркотики и запрещенные вещества": {
                "ru": [
                    "Продажа наркотиков через Telegram. Пользователь {user_id} рекламирует запрещенные вещества. Контент: {violation_link}",
                    "Распространение рецептов изготовления наркотиков. Пользователь @{username} (ID: {user_id}). Инструкции: {violation_link}",
                    "Создание каналов для торговли наркотиками. Администратор {user_id}. Канал: {violation_link}",
                    "Реклама синтетических наркотиков и солей. Пользователь {user_id} нарушает законодательство. Сообщения: {violation_link}",
                    "Продажа рецептурных препаратов без рецепта. Пользователь {user_id} занимается незаконной фармацевтикой. Доказательства: {violation_link}",
                    "Распространение информации о местах сбыта наркотиков. Пользователь @{username} (ID: {user_id}). Список точек: {violation_link}",
                    "Создание групп для обсуждения употребления наркотиков. Пользователь {user_id}. Группа: {violation_link}",
                    "Реклама услуг по доставке наркотиков курьером. Пользователь {user_id} организует преступную сеть. Контент: {violation_link}",
                    "Продажа оборудования для нарколабораторий. Пользователь {user_id} нарушает закон. Объявления: {violation_link}",
                    "Распространение информации об обходе наркоконтроля. Пользователь @{username} (ID: {user_id}). Советы: {violation_link}",
                    "Создание каналов с отзывами о наркотиках. Администратор {user_id}. Канал: {violation_link}",
                    "Продажа семян запрещенных растений. Пользователь {user_id} нарушает законодательство. Товары: {violation_link}",
                    "Реклама наркотиков под видом БАДов. Пользователь {user_id} обманывает покупателей. Контент: {violation_link}",
                    "Распространение информации о легальных аналогах наркотиков. Пользователь @{username} (ID: {user_id}). Материалы: {violation_link}",
                    "Создание групп для поиска наркодилеров. Пользователь {user_id}. Группа: {violation_link}",
                    "Продажа тестов на наркотики с подделкой результатов. Пользователь {user_id} мошенничает. Услуги: {violation_link}",
                    "Реклама наркотиков в школьных чатах. Пользователь {user_id} нацелен на несовершеннолетних. Доказательства: {violation_link}",
                    "Распространение информации о чистке организма от наркотиков. Пользователь @{username} (ID: {user_id}). Методы: {violation_link}",
                    "Создание каналов с ценами на наркорынке. Администратор {user_id}. Канал: {violation_link}",
                    "Продажа книг по выращиванию наркорастений. Пользователь {user_id}. Литература: {violation_link}",
                ],
                "en": [
                    "Drug sales via Telegram. User {user_id} advertises illegal substances. Content: {violation_link}",
                    "Distribution of drug manufacturing recipes. User @{username} (ID: {user_id}). Instructions: {violation_link}",
                    "Channel creation for drug trade. Admin {user_id}. Channel: {violation_link}",
                    "Advertising of synthetic drugs and salts. User {user_id} violates laws. Messages: {violation_link}",
                    "Sale of prescription drugs without prescription. User {user_id} engages in illegal pharmaceuticals. Evidence: {violation_link}",
                    "Distribution of drug selling location information. User @{username} (ID: {user_id}). Location list: {violation_link}",
                    "Group creation for drug use discussion. User {user_id}. Group: {violation_link}",
                    "Advertising of drug delivery services. User {user_id} organizes criminal network. Content: {violation_link}",
                    "Sale of drug lab equipment. User {user_id} breaks law. Listings: {violation_link}",
                    "Distribution of drug control bypass information. User @{username} (ID: {user_id}). Tips: {violation_link}",
                    "Channel creation with drug reviews. Admin {user_id}. Channel: {violation_link}",
                    "Sale of banned plant seeds. User {user_id} violates legislation. Products: {violation_link}",
                    "Advertising of drugs disguised as supplements. User {user_id} deceives buyers. Content: {violation_link}",
                    "Distribution of legal drug analog information. User @{username} (ID: {user_id}). Materials: {violation_link}",
                    "Group creation for finding drug dealers. User {user_id}. Group: {violation_link}",
                    "Sale of drug tests with result falsification. User {user_id} scams. Services: {violation_link}",
                    "Drug advertising in school chats. User {user_id} targets minors. Evidence: {violation_link}",
                    "Distribution of drug cleansing information. User @{username} (ID: {user_id}). Methods: {violation_link}",
                    "Channel creation with drug market prices. Admin {user_id}. Channel: {violation_link}",
                    "Sale of drug plant cultivation books. User {user_id}. Literature: {violation_link}",
                ]
            },
            "Пиратство и нарушение авторских прав": {
                "ru": [
                    "Распространение пиратского контента. Пользователь {user_id} делится нелицензионными фильмами. Ссылки: {violation_link}",
                    "Создание каналов с пиратскими книгами и аудиокнигами. Администратор {user_id}. Канал: {violation_link}",
                    "Продажа взломанных аккаунтов Netflix и Spotify. Пользователь @{username} (ID: {user_id}). Объявления: {violation_link}",
                    "Распространение взломанного программного обеспечения. Пользователь {user_id} нарушает авторские права. Файлы: {violation_link}",
                    "Создание групп для обмена пиратскими ключами игр. Пользователь {user_id}. Группа: {violation_link}",
                    "Продажа поддельных лицензий Windows и Office. Пользователь {user_id} занимается контрафактом. Доказательства: {violation_link}",
                    "Распространение платных курсов без разрешения авторов. Пользователь @{username} (ID: {user_id}). Материалы: {violation_link}",
                    "Создание каналов с утечками платного контента OnlyFans. Администратор {user_id}. Канал: {violation_link}",
                    "Продажа взломанных баз данных и слитой информации. Пользователь {user_id} нарушает законы о персональных данных. Контент: {violation_link}",
                    "Распространение плагиата и копирование чужих работ. Пользователь {user_id} выдает чужие работы за свои. Примеры: {violation_link}",
                    "Создание групп для торговли контрафактными товарами. Пользователь {user_id}. Группа: {violation_link}",
                    "Продажа поддельных сертификатов и дипломов. Пользователь @{username} (ID: {user_id}). Услуги: {violation_link}",
                    "Распространение взломанных мобильных приложений. Пользователь {user_id} делится Mod APK. Файлы: {violation_link}",
                    "Создание каналов с платными статьями без подписки. Администратор {user_id}. Канал: {violation_link}",
                    "Продажа доступа к платным ресурсам через общие аккаунты. Пользователь {user_id} нарушает условия сервисов. Предложения: {violation_link}",
                    "Распространение пиратских переводов фильмов и сериалов. Пользователь {user_id} ворует работу переводчиков. Контент: {violation_link}",
                    "Создание групп для обмена платными научными статьями. Пользователь @{username} (ID: {user_id}). Группа: {violation_link}",
                    "Продажа поддельных ключей активации для игр. Пользователь {user_id} мошенничает с лицензиями. Доказательства: {violation_link}",
                    "Распространение платных шаблонов сайтов без лицензии. Пользователь {user_id}. Файлы: {violation_link}",
                    "Создание каналов с утечками платных отчетов и исследований. Администратор {user_id}. Канал: {violation_link}",
                ],
                "en": [
                    "Pirated content distribution. User {user_id} shares unlicensed movies. Links: {violation_link}",
                    "Channel creation with pirated books and audiobooks. Admin {user_id}. Channel: {violation_link}",
                    "Sale of hacked Netflix and Spotify accounts. User @{username} (ID: {user_id}). Listings: {violation_link}",
                    "Distribution of cracked software. User {user_id} violates copyrights. Files: {violation_link}",
                    "Group creation for pirated game key exchange. User {user_id}. Group: {violation_link}",
                    "Sale of fake Windows and Office licenses. User {user_id} deals in counterfeit. Evidence: {violation_link}",
                    "Distribution of paid courses without author permission. User @{username} (ID: {user_id}). Materials: {violation_link}",
                    "Channel creation with leaked OnlyFans content. Admin {user_id}. Channel: {violation_link}",
                    "Sale of hacked databases and leaked information. User {user_id} violates data protection laws. Content: {violation_link}",
                    "Distribution of plagiarism and copied works. User {user_id} presents others' work as own. Examples: {violation_link}",
                    "Group creation for counterfeit goods trade. User {user_id}. Group: {violation_link}",
                    "Sale of fake certificates and diplomas. User @{username} (ID: {user_id}). Services: {violation_link}",
                    "Distribution of cracked mobile apps. User {user_id} shares Mod APK. Files: {violation_link}",
                    "Channel creation with paid articles without subscription. Admin {user_id}. Channel: {violation_link}",
                    "Sale of access to paid resources via shared accounts. User {user_id} violates service terms. Offers: {violation_link}",
                    "Distribution of pirated movie/TV show translations. User {user_id} steals translators' work. Content: {violation_link}",
                    "Group creation for paid scientific article exchange. User @{username} (ID: {user_id}). Group: {violation_link}",
                    "Sale of fake game activation keys. User {user_id} scams with licenses. Evidence: {violation_link}",
                    "Distribution of paid website templates without license. User {user_id}. Files: {violation_link}",
                    "Channel creation with leaked paid reports and research. Admin {user_id}. Channel: {violation_link}",
                ]
            },
            "Незаконная торговля": {
                "ru": [
                    "Торговля оружием через Telegram. Пользователь {user_id} продает огнестрельное оружие нелегально. Контент: {violation_link}",
                    "Продажа поддельных документов: паспортов, водительских прав. Пользователь @{username} (ID: {user_id}). Объявления: {violation_link}",
                    "Торговля украденными вещами и крадеными товарами. Пользователь {user_id} сбывает ворованное. Каталог: {violation_link}",
                    "Продажа диких животных и краснокнижных видов. Пользователь {user_id} нарушает природоохранное законодательство. Предложения: {violation_link}",
                    "Торговля человеческими органами. Пользователь {user_id} занимается черной трансплантологией. Доказательства: {violation_link}",
                    "Продажа поддельных денег и фальшивых купюр. Пользователь @{username} (ID: {user_id}). Услуги: {violation_link}",
                    "Торговля крадеными данными кредитных карт. Пользователь {user_id} продает базы карт. Контент: {violation_link}",
                    "Продажа радиоактивных материалов и веществ. Пользователь {user_id} нарушает законы о безопасности. Предложения: {violation_link}",
                    "Торговля крадеными телефонами и гаджетами. Пользователь {user_id} сбывает технику без боксов. Каталог: {violation_link}",
                    "Продажа поддельных лекарств и фальсификатов. Пользователь @{username} (ID: {user_id}) рискует жизнями людей. Товары: {violation_link}",
                    "Торговля крадеными автомобилями и запчастями. Пользователь {user_id} занимается угоном. Предложения: {violation_link}",
                    "Продажа взрывчатых веществ и пиротехники без лицензии. Пользователь {user_id} нарушает правила безопасности. Контент: {violation_link}",
                    "Торговля контрабандными сигаретами и алкоголем. Пользователь {user_id} уклоняется от налогов. Каталог: {violation_link}",
                    "Продажа краденых произведений искусства. Пользователь @{username} (ID: {user_id}) торгует украденными картинами. Фото: {violation_link}",
                    "Торговля запрещенными химическими веществами. Пользователь {user_id} продает прекурсоры наркотиков. Список: {violation_link}",
                    "Продажа поддельных брендовых вещей. Пользователь {user_id} торгует контрафактной одеждой. Каталог: {violation_link}",
                    "Торговля крадеными данными для доступа к аккаунтам. Пользователь {user_id} продает логины и пароли. Базы: {violation_link}",
                    "Продажа человеческих волос и органов без разрешения. Пользователь @{username} (ID: {user_id}) нарушает этические нормы. Предложения: {violation_link}",
                    "Торговля историческими артефактами нелегально. Пользователь {user_id} продает украденные музейные экспонаты. Фото: {violation_link}",
                    "Продажа поддельных справок и медицинских документов. Пользователь {user_id} занимается подлогом. Услуги: {violation_link}",
                ],
                "en": [
                    "Weapon trade via Telegram. User {user_id} sells firearms illegally. Content: {violation_link}",
                    "Sale of fake documents: passports, driver's licenses. User @{username} (ID: {user_id}). Listings: {violation_link}",
                    "Trade of stolen goods and robbed items. User {user_id} fences stolen property. Catalog: {violation_link}",
                    "Sale of wild animals and endangered species. User {user_id} violates conservation laws. Offers: {violation_link}",
                    "Human organ trade. User {user_id} engages in black transplantology. Evidence: {violation_link}",
                    "Sale of counterfeit money and fake banknotes. User @{username} (ID: {user_id}). Services: {violation_link}",
                    "Trade of stolen credit card data. User {user_id} sells card databases. Content: {violation_link}",
                    "Sale of radioactive materials and substances. User {user_id} violates safety laws. Offers: {violation_link}",
                    "Trade of stolen phones and gadgets. User {user_id} sells devices without boxes. Catalog: {violation_link}",
                    "Sale of fake medicines and counterfeit drugs. User @{username} (ID: {user_id}) risks lives. Products: {violation_link}",
                    "Trade of stolen cars and auto parts. User {user_id} deals in car theft. Offers: {violation_link}",
                    "Sale of explosives and pyrotechnics without license. User {user_id} violates safety rules. Content: {violation_link}",
                    "Trade of smuggled cigarettes and alcohol. User {user_id} evades taxes. Catalog: {violation_link}",
                    "Sale of stolen art works. User @{username} (ID: {user_id}) trades stolen paintings. Photos: {violation_link}",
                    "Trade of banned chemical substances. User {user_id} sells drug precursors. List: {violation_link}",
                    "Sale of counterfeit brand goods. User {user_id} trades fake clothing. Catalog: {violation_link}",
                    "Trade of stolen account access data. User {user_id} sells logins and passwords. Databases: {violation_link}",
                    "Sale of human hair and organs without permission. User @{username} (ID: {user_id}) violates ethics. Offers: {violation_link}",
                    "Illegal trade of historical artifacts. User {user_id} sells stolen museum exhibits. Photos: {violation_link}",
                    "Sale of fake certificates and medical documents. User {user_id} engages in forgery. Services: {violation_link}",
                ]
            },
            "Порнография и взрослый контент": {
                "ru": [
                    "Распространение порнографии в общих чатах. Пользователь {user_id} нарушает правила сообщества. Контент: {violation_link}",
                    "Создание каналов с запрещенным взрослым контентом. Администратор {user_id}. Канал: {violation_link}",
                    "Публикация интимных фото без согласия людей. Пользователь @{username} (ID: {user_id}) нарушает приватность. Материалы: {violation_link}",
                    "Распространение экстремального и насильственного порно. Пользователь {user_id} делится незаконным контентом. Видео: {violation_link}",
                    "Создание групп для обмена приватными фото несовершеннолетних. Пользователь {user_id}. Группа: {violation_link}",
                    "Публикация платного контента OnlyFans бесплатно. Пользователь {user_id} ворует материалы. Контент: {violation_link}",
                    "Распространение порно с животными (зоофилия). Пользователь @{username} (ID: {user_id}) нарушает законы. Материалы: {violation_link}",
                    "Создание каналов с утечками интимных переписок знаменитостей. Администратор {user_id}. Канал: {violation_link}",
                    "Публикация порно в публичных группах без предупреждения. Пользователь {user_id} шокирует участников. Контент: {violation_link}",
                    "Распространение материалов инцеста и кровосмешения. Пользователь {user_id} делится запрещенным контентом. Видео: {violation_link}",
                    "Создание групп для торговли интимными услугами. Пользователь @{username} (ID: {user_id}). Группа: {violation_link}",
                    "Публикация порно с несовершеннолетними (детская порнография). Пользователь {user_id} совершает преступление. Материалы: {violation_link}",
                    "Распространение сцен некрофилии и танатофилии. Пользователь {user_id} нарушает все нормы морали. Контент: {violation_link}",
                    "Создание каналов с подглядыванием и вуайеризмом. Администратор {user_id}. Канал: {violation_link}",
                    "Публикация интимных фото бывших партнеров без согласия. Пользователь {user_id} мстит бывшим. Материалы: {violation_link}",
                    "Распространение порно с участием наркотиков. Пользователь @{username} (ID: {user_id}) пропагандирует опасный контент. Видео: {violation_link}",
                    "Создание групп для обмена фото обнаженных незнакомцев. Пользователь {user_id}. Группа: {violation_link}",
                    "Публикация порно в группах для несовершеннолетних. Пользователь {user_id} развращает детей. Контент: {violation_link}",
                    "Распространение материалов с сексуальным насилием и изнасилованиями. Пользователь {user_id} нарушает закон. Видео: {violation_link}",
                    "Создание каналов с поддельными нюдсами знаменитостей (deepfake). Администратор {user_id}. Канал: {violation_link}",
                ],
                "en": [
                    "Pornography distribution in public chats. User {user_id} violates community rules. Content: {violation_link}",
                    "Channel creation with prohibited adult content. Admin {user_id}. Channel: {violation_link}",
                    "Publication of intimate photos without consent. User @{username} (ID: {user_id}) violates privacy. Materials: {violation_link}",
                    "Distribution of extreme and violent porn. User {user_id} shares illegal content. Video: {violation_link}",
                    "Group creation for exchanging minors' private photos. User {user_id}. Group: {violation_link}",
                    "Publication of paid OnlyFans content for free. User {user_id} steals materials. Content: {violation_link}",
                    "Distribution of animal porn (zoophilia). User @{username} (ID: {user_id}) breaks laws. Materials: {violation_link}",
                    "Channel creation with celebrity intimate chat leaks. Admin {user_id}. Channel: {violation_link}",
                    "Publication of porn in public groups without warning. User {user_id} shocks members. Content: {violation_link}",
                    "Distribution of incest and inbreeding materials. User {user_id} shares prohibited content. Video: {violation_link}",
                    "Group creation for intimate service trade. User @{username} (ID: {user_id}). Group: {violation_link}",
                    "Publication of underage porn (child pornography). User {user_id} commits crime. Materials: {violation_link}",
                    "Distribution of necrophilia and thanatophilia scenes. User {user_id} violates all moral norms. Content: {violation_link}",
                    "Channel creation with voyeurism and peeping content. Admin {user_id}. Channel: {violation_link}",
                    "Publication of ex-partners' intimate photos without consent. User {user_id} seeks revenge. Materials: {violation_link}",
                    "Distribution of drug-involved porn. User @{username} (ID: {user_id}) promotes dangerous content. Video: {violation_link}",
                    "Group creation for exchanging strangers' nude photos. User {user_id}. Group: {violation_link}",
                    "Publication of porn in minors' groups. User {user_id} corrupts children. Content: {violation_link}",
                    "Distribution of sexual violence and rape materials. User {user_id} breaks law. Video: {violation_link}",
                    "Channel creation with celebrity fake nudes (deepfake). Admin {user_id}. Channel: {violation_link}",
                ]
            },
            "Фейковые новости и дезинформация": {
                "ru": [
                    "Распространение фейковых новостей о COVID-19. Пользователь {user_id} вводит людей в заблуждение. Контент: {violation_link}",
                    "Создание каналов с ложной медицинской информацией. Администратор {user_id}. Канал: {violation_link}",
                    "Публикация фейковых новостей о политических событиях. Пользователь @{username} (ID: {user_id}) манипулирует общественным мнением. Статьи: {violation_link}",
                    "Распространение ложной информации о вакцинах. Пользователь {user_id} опасен для общественного здоровья. Контент: {violation_link}",
                    "Создание групп для координации информационных атак. Пользователь {user_id}. Группа: {violation_link}",
                    "Публикация поддельных документов и указов. Пользователь {user_id} распространяет фейки. Документы: {violation_link}",
                    "Распространение ложной информации о финансовых рынках. Пользователь @{username} (ID: {user_id}) манипулирует курсами. Сообщения: {violation_link}",
                    "Создание каналов с фейковыми прогнозами катастроф. Администратор {user_id}. Канал: {violation_link}",
                    "Публикация поддельных новостей от имени официальных СМИ. Пользователь {user_id} нарушает закон. Контент: {violation_link}",
                    "Распространение ложной информации о военных действиях. Пользователь {user_id} сеет панику. Сообщения: {violation_link}",
                    "Создание групп для распространения теорий заговора. Пользователь @{username} (ID: {user_id}). Группа: {violation_link}",
                    "Публикация фейковых интервью с политиками. Пользователь {user_id} использует deepfake. Видео: {violation_link}",
                    "Распространение ложной информации о стихийных бедствиях. Пользователь {user_id} вызывает необоснованную панику. Контент: {violation_link}",
                    "Создание каналов с поддельными научными исследованиями. Администратор {user_id}. Канал: {violation_link}",
                    "Публикация фейковых новостей о смерти знаменитостей. Пользователь {user_id} распространяет слухи. Статьи: {violation_link}",
                    "Распространение ложной информации о продуктах питания. Пользователь @{username} (ID: {user_id}) вредит бизнесу компаний. Контент: {violation_link}",
                    "Создание групп для координации дезинформационных кампаний. Пользователь {user_id}. Группа: {violation_link}",
                    "Публикация поддельных экономических прогнозов. Пользователь {user_id} манипулирует инвесторами. Отчеты: {violation_link}",
                    "Распространение ложной информации о выборах. Пользователь {user_id} подрывает доверие к институтам. Контент: {violation_link}",
                    "Создание каналов с фейковыми сенсационными открытиями. Администратор {user_id}. Канал: {violation_link}",
                ],
                "en": [
                    "Distribution of fake COVID-19 news. User {user_id} misleads people. Content: {violation_link}",
                    "Channel creation with false medical information. Admin {user_id}. Channel: {violation_link}",
                    "Publication of fake political event news. User @{username} (ID: {user_id}) manipulates public opinion. Articles: {violation_link}",
                    "Distribution of false vaccine information. User {user_id} dangerous for public health. Content: {violation_link}",
                    "Group creation for coordinating information attacks. User {user_id}. Group: {violation_link}",
                    "Publication of fake documents and decrees. User {user_id} spreads fakes. Documents: {violation_link}",
                    "Distribution of false financial market information. User @{username} (ID: {user_id}) manipulates rates. Messages: {violation_link}",
                    "Channel creation with fake disaster predictions. Admin {user_id}. Channel: {violation_link}",
                    "Publication of fake news in name of official media. User {user_id} breaks law. Content: {violation_link}",
                    "Distribution of false military action information. User {user_id} spreads panic. Messages: {violation_link}",
                    "Group creation for spreading conspiracy theories. User @{username} (ID: {user_id}). Group: {violation_link}",
                    "Publication of fake politician interviews. User {user_id} uses deepfake. Video: {violation_link}",
                    "Distribution of false natural disaster information. User {user_id} causes unwarranted panic. Content: {violation_link}",
                    "Channel creation with fake scientific research. Admin {user_id}. Channel: {violation_link}",
                    "Publication of fake celebrity death news. User {user_id} spreads rumors. Articles: {violation_link}",
                    "Distribution of false food product information. User @{username} (ID: {user_id}) harms companies' business. Content: {violation_link}",
                    "Group creation for coordinating disinformation campaigns. User {user_id}. Group: {violation_link}",
                    "Publication of fake economic forecasts. User {user_id} manipulates investors. Reports: {violation_link}",
                    "Distribution of false election information. User {user_id} undermines institutional trust. Content: {violation_link}",
                    "Channel creation with fake sensational discoveries. Admin {user_id}. Channel: {violation_link}",
                ]
            }
        }

    def get_random_user_agent(self):
        """Случайный User-Agent"""
        agents = [
            # Chrome Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Firefox Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            # Safari Mac
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            # Mobile iOS
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        ]
        return random.choice(agents)

    def generate_email(self):
        """Генерация случайного email"""
        domains = ["gmail.com", "outlook.com", "yahoo.com", "mail.ru", "yandex.ru"]
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{username}@{random.choice(domains)}"

    def generate_phone(self):
        """Генерация случайного номера телефона"""
        return f"+79{''.join(random.choices('0123456789', k=9))}"

    def prepare_form_data(self, complaint_text, lang):
        """Подготовка данных формы в правильном формате"""
        if lang == "ru":
            # РУССКАЯ ФОРМА (важно!)
            return {
                'tg_feedback_appeal': complaint_text,  # Основное поле
                'tg_feedback_email': self.generate_email(),  # Email поле
                'tg_feedback_phone': self.generate_phone(),  # Телефон поле
                'setln': 'ru'  # Язык интерфейса
            }
        else:
            # АНГЛИЙСКАЯ ФОРМА
            return {
                'message': complaint_text,  # Основное поле
                'email': self.generate_email(),  # Email поле
                'phone': self.generate_phone(),  # Телефон поле
                'setln': 'en'  # Язык интерфейса
            }

    def get_target_url(self, lang):
        """Получение правильного URL"""
        if lang == "ru":
            return "https://telegram.org/support?setln=ru"
        else:
            return "https://telegram.org/support"

    def get_form_headers(self, lang, url):
        """Получение правильных заголовков для формы"""
        if lang == "ru":
            return {
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://telegram.org',
                'Referer': url,
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'Connection': 'keep-alive',
            }
        else:
            return {
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://telegram.org',
                'Referer': url,
                'DNT': '1',
                'Connection': 'keep-alive',
            }

    def analyze_response(self, response, lang):
        """Анализ ответа сервера"""
        try:
            text = response.text
            text_lower = text.lower()

            # Ключевые слова успеха для каждого языка
            success_keywords = {
                'ru': ['спасибо', 'получили', 'отправлено', 'жалоба принята',
                       'успешно', 'принято', 'обращение зарегистрировано'],
                'en': ['thank you', 'received', 'submitted', 'success',
                       'complaint registered', 'sent successfully', 'message has been']
            }

            # Проверяем успешные ключевые слова
            for keyword in success_keywords[lang]:
                if keyword in text_lower:
                    return True

            # Дополнительные проверки
            if response.status_code != 200:
                return False

            # Если получили ту же форму обратно - ошибка
            if lang == "ru":
                if 'tg_feedback_appeal' in text and len(text) < 10000:
                    return False
            else:
                if 'name="message"' in text and len(text) < 10000:
                    return False

            # Если ответ длинный и содержит "telegram" - возможно успех
            if 'telegram' in text_lower and len(text) > 3000:
                return True

            return False

        except Exception as e:
            self.log_event("ERROR", f"Ошибка анализа ответа: {e}")
            return False

    def send_complaint(self, user_data, attempt_number):
        """Отправка одной жалобы"""
        try:
            # Определяем язык отправки
            if self.force_language == "ru":
                lang = "ru"
            elif self.force_language == "en":
                lang = "en"
            else:
                # Случайный выбор
                lang = "ru" if attempt_number % 2 == 0 else "en"

            # Получаем URL и заголовки
            url = self.get_target_url(lang)
            headers = self.get_form_headers(lang, url)

            # Выбираем шаблон на нужном языке
            templates = self.complaint_templates[user_data['complaint_type']][lang]
            template = random.choice(templates)

            # Форматируем текст
            complaint_text = template.format(
                user_id=user_data['user_id'],
                username=user_data['username'],
                violation_link=user_data['violation_link']
            )

            # Обрезаем если слишком длинный
            if len(complaint_text) > 1500:
                complaint_text = complaint_text[:1500] + "..."

            # Подготавливаем данные формы
            form_data = self.prepare_form_data(complaint_text, lang)

            # Логируем что отправляем
            self.log_event("INFO", f"Отправка #{attempt_number + 1} на языке {lang}")
            self.log_event("DEBUG", f"URL: {url}")
            self.log_event("DEBUG", f"Поля формы: {list(form_data.keys())}")

            # Отправляем запрос (ИСПРАВЛЕНО: убрано дублирование allow_redirects)
            response = self.session.post(
                url,
                data=form_data,
                headers=headers,
                timeout=20,
                allow_redirects=True
            )

            self.stats['total_sent'] += 1

            # Анализируем ответ
            is_success = self.analyze_response(response, lang)

            # Логируем результат
            if is_success:
                self.stats['successful'] += 1
                self.log_event("SUCCESS", f"Жалоба #{attempt_number + 1} отправлена успешно")
                return True, f"✅ {lang.upper()} | Статус: {response.status_code}"
            else:
                self.stats['failed'] += 1
                self.log_event("WARNING", f"Жалоба #{attempt_number + 1} не отправлена")

                # Сохраняем ошибку для анализа
                self.save_error_response(response, attempt_number, form_data, headers, url, lang)

                return False, f"❌ {lang.upper()} | Статус: {response.status_code}"

        except Exception as e:
            self.stats['failed'] += 1
            self.log_event("ERROR", f"Ошибка при отправке: {str(e)}")
            return False, f"🚫 Ошибка: {str(e)[:50]}"

    def save_error_response(self, response, attempt_number, form_data, headers, url, lang):
        """Сохранение ошибочного ответа"""
        try:
            error_dir = os.path.join(self.log_dir, "error_responses")
            os.makedirs(error_dir, exist_ok=True)

            filename = os.path.join(error_dir, f"error_{lang}_{attempt_number}.html")

            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"ЯЗЫК: {lang}\n")
                f.write(f"URL: {url}\n")
                f.write(f"Статус: {response.status_code}\n")
                f.write("=" * 80 + "\n\n")

                f.write("ДАННЫЕ ФОРМЫ:\n")
                f.write("-" * 40 + "\n")
                for key, value in form_data.items():
                    f.write(f"{key}: {value}\n")
                f.write("\n")

                f.write("ОТВЕТ (первые 3000 символов):\n")
                f.write("-" * 40 + "\n")
                f.write(response.text[:3000])

            self.log_event("DEBUG", f"Сохранена ошибка в файл: {filename}")

        except Exception as e:
            self.log_event("ERROR", f"Не удалось сохранить ошибку: {e}")

    def get_user_input(self):
        """Получение данных от пользователя"""
        os.system('cls' if os.name == 'nt' else 'clear')

        print(Fore.CYAN + """
╔══════════════════════════════════════════╗
║    ИСПРАВЛЕННЫЙ ТЕЛЕГРАМ БОТ ДЛЯ ЖАЛОБ  ║
╚══════════════════════════════════════════╝
        """ + Style.RESET_ALL)

        print(Fore.YELLOW + "[!] Используйте только для реальных нарушений!\n" + Style.RESET_ALL)

        # ID пользователя
        user_id = ""
        while not user_id.isdigit() or len(user_id) < 5:
            user_id = input(Fore.GREEN + "ID нарушителя (только цифры): " + Style.RESET_ALL).strip()
            if not user_id.isdigit():
                print(Fore.RED + "Только цифры!" + Style.RESET_ALL)

        # Username
        username = input(Fore.GREEN + "@username (без @, Enter если нет): " + Style.RESET_ALL).strip()
        if username:
            username = f"@{username}"
        else:
            username = f"user_{user_id}"

        # Ссылка на нарушение
        violation_link = input(Fore.GREEN + "Ссылка на нарушение: " + Style.RESET_ALL).strip()
        if not violation_link:
            violation_link = "https://t.me/..."

        # Выбор типа жалобы
        print(Fore.GREEN + "\nТип жалобы:" + Style.RESET_ALL)
        categories = list(self.complaint_templates.keys())
        for i, category in enumerate(categories, 1):
            print(f"  {i}. {category}")

        while True:
            try:
                choice = int(input(Fore.GREEN + "Выберите номер: " + Style.RESET_ALL))
                if 1 <= choice <= len(categories):
                    complaint_type = categories[choice - 1]
                    break
                else:
                    print(Fore.RED + f"Выберите от 1 до {len(categories)}" + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Введите число!" + Style.RESET_ALL)

        # Количество жалоб
        while True:
            try:
                count = int(input(Fore.GREEN + "Количество жалоб (1-10): " + Style.RESET_ALL))
                if 1 <= count <= 10:
                    request_count = count
                    break
                else:
                    print(Fore.RED + "От 1 до 10!" + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Введите число!" + Style.RESET_ALL)

        # Язык отправки
        print(Fore.GREEN + "\nЯзык отправки:" + Style.RESET_ALL)
        print("  1. Случайный (рекомендуется)")
        print("  2. Только русский")
        print("  3. Только английский")

        lang_choice = input(Fore.GREEN + "Выберите опцию (1-3): " + Style.RESET_ALL) or "1"

        if lang_choice == "2":
            self.force_language = "ru"
        elif lang_choice == "3":
            self.force_language = "en"
        else:
            self.force_language = "random"

        return {
            'user_id': user_id,
            'username': username,
            'violation_link': violation_link,
            'complaint_type': complaint_type,
            'request_count': request_count
        }

    def check_internet(self):
        """Проверка интернета"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            return True
        except:
            return False

    def run(self):
        """Основной цикл"""
        if not self.check_internet():
            print(Fore.RED + "\nНет интернета!" + Style.RESET_ALL)
            input("Нажмите Enter...")
            return

        try:
            user_data = self.get_user_input()
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nОтменено" + Style.RESET_ALL)
            return

        print(Fore.GREEN + "\n" + "=" * 50 + Style.RESET_ALL)
        print(Fore.YELLOW + "ИНФОРМАЦИЯ О ЦЕЛИ:" + Style.RESET_ALL)
        print(Fore.CYAN + f"  ID: {user_data['user_id']}")
        print(f"  Username: {user_data['username']}")
        print(f"  Тип: {user_data['complaint_type']}")
        print(f"  Количество: {user_data['request_count']}")
        print(f"  Язык: {'Случайный' if self.force_language == 'random' else self.force_language}")
        print(Fore.GREEN + "=" * 50 + Style.RESET_ALL)

        print(Fore.YELLOW + "\nНачинаю отправку...\n" + Style.RESET_ALL)

        # Подготовка сессии
        print(Fore.CYAN + "[*] Подготовка..." + Style.RESET_ALL)
        try:
            self.session.get("https://telegram.org/", timeout=10)
            time.sleep(2)
        except:
            print(Fore.YELLOW + "[!] Проблемы с подключением" + Style.RESET_ALL)

        start_time = time.time()

        for i in range(user_data['request_count']):
            print(Fore.CYAN + f"\n[{i + 1}/{user_data['request_count']}] Отправка..." + Style.RESET_ALL)

            success, message = self.send_complaint(user_data, i)

            if success:
                print(Fore.GREEN + f"  {message}" + Style.RESET_ALL)
            else:
                print(Fore.RED + f"  {message}" + Style.RESET_ALL)

            # Большая задержка между запросами
            if i < user_data['request_count'] - 1:
                delay = random.uniform(10, 20)
                print(Fore.CYAN + f"  Задержка: {delay:.1f} сек..." + Style.RESET_ALL)
                time.sleep(delay)

        # Статистика
        duration = time.time() - start_time

        print(Fore.CYAN + "\n" + "=" * 50 + Style.RESET_ALL)
        print(Fore.YELLOW + "СТАТИСТИКА:" + Style.RESET_ALL)
        print(Fore.GREEN + f"  Успешно: {self.stats['successful']}")
        print(Fore.RED + f"  Ошибки: {self.stats['failed']}")
        print(Fore.CYAN + f"  Всего: {self.stats['total_sent']}")
        print(Fore.CYAN + f"  Время: {duration:.1f} сек")
        print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)

        if self.stats['successful'] > 0:
            print(Fore.GREEN + "\n✓ Часть жалоб отправлена!" + Style.RESET_ALL)
        else:
            print(Fore.RED + "\n✗ Не удалось отправить жалобы" + Style.RESET_ALL)
            print(Fore.YELLOW + "Попробуйте:" + Style.RESET_ALL)
            print("  1. Использовать VPN")
            print("  2. Уменьшить количество до 2-3")
            print("  3. Увеличить задержки")

        print(Fore.CYAN + f"\nЛог-файл: {self.log_file}" + Style.RESET_ALL)
        input("\nНажмите Enter для выхода...")


def main():
    try:
        bot = FixedTelegramComplaintBot()
        bot.run()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nОстановлено" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"\nОшибка: {e}" + Style.RESET_ALL)
        input("Нажмите Enter...")


if __name__ == "__main__":
    main()