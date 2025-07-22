import asyncio
from bot.loader import bot
from bot.utils.database.functions import f_user

async def send_message_to_user(user_id, from_id, message_id, reply_markup):
    try:
        await bot.copy_message(user_id, from_id, message_id, reply_markup=reply_markup)
        print("✅✅✅", user_id, "ga yuborildi")
        return 1, 0
    except Exception as e:
        return await handle_send_error(user_id, from_id, message_id, reply_markup, e)


async def handle_send_error(user_id, from_id, message_id, reply_markup, exception):
    error_message = str(exception).lower()

    if any(x in error_message for x in ["blocked", "deactivated", "not found"]):
        print("❌❌❌", user_id, "ga bormadi!!!! \n", error_message)
        await f_user.update_user(user_id, is_blocked=True)
        return 0, 1

    if "flood control" in error_message or "too many requests" in error_message:
        try:
            sleep_time = int(error_message.split()[-2])
        except:
            sleep_time = 10
        print("💤💤💤 ", sleep_time, " sekundga pauza bo'ldi\n", error_message)
        await asyncio.sleep(sleep_time)
        return await send_message_to_user(user_id, from_id, message_id, reply_markup)

    print("⭕️⭕️⭕️⭕️", user_id, "\n", error_message)
    return 0, 0


async def process_user_group(users, from_id, message_id, reply_markup):
    count_sent, count_blocked = 0, 0
    for user_id in users:
        sent, blocked = await send_message_to_user(user_id, from_id, message_id, reply_markup)
        count_sent += sent
        count_blocked += blocked
    return count_sent, count_blocked


async def distribute_message(users, user_id, message_id, reply_markup, group_size=40, delay=1):
    total_users = len(users)
    count = total_users // group_size
    last_group_size = total_users % group_size

    tasks = []
    for i in range(group_size):
        start_index = i * count
        end_index = start_index + count
        tasks.append(asyncio.create_task(
            process_user_group(users[start_index:end_index], user_id, message_id, reply_markup)
        ))
        await asyncio.sleep(delay)

    if last_group_size > 0:
        tasks.append(asyncio.create_task(
            process_user_group(users[-last_group_size:], user_id, message_id, reply_markup)
        ))

    results = await asyncio.gather(*tasks)
    return sum(r[0] for r in results), sum(r[1] for r in results)
