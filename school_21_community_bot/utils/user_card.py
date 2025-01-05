def create_user_card(user_data):
    return (
        f"""
        Проверьте введенные данные:

        Ник в Школе 21: {user_data.get('school21_nick')}
        Имя в Сберчате: {user_data.get('sberchat_nick')}
        Ник в Telegram: @{user_data.get('telegram_nick')}
        Название команды: {user_data.get('team')}
        Ваша роль: {user_data.get('role')}
        Ваш уровень: {user_data.get('level')}
        Над чем вы работаете: {user_data.get('project')}

        """
    )
