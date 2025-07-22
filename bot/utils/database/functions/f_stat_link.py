from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.utils.database.models import SocialNetworkStat, engine

async def get_social_network_stats(session) -> dict:
    result = await session.execute(
        select(SocialNetworkStat)
    )
    stats = result.scalar_one_or_none()
    if not stats:
        return None

    return {
        "Facebook": stats.facebook,
        "Instagram": stats.instagram,
        "YouTube": stats.youtube,
        "TikTok": stats.tiktok,
        "Telegram": stats.telegram,
        "Twitter": stats.twitter,
        "VK": stats.vk,
        "OK": stats.ok,
        "LinkedIn": stats.linkedin,
        "Reddit": stats.reddit,
        "Snapchat": stats.snapchat,
        "Pinterest": stats.pinterest,
        "Tumblr": stats.tumblr,
        "Threads": stats.threads,
        "Weibo": stats.weibo,
        "WeChat": stats.wechat,
        "Track": stats.track,  # 👉 YANGI USTUN
    }


def detect_social_network(link: str) -> str:
    link = link.lower()
    if "facebook.com" in link:
        return "facebook"
    elif "instagram.com" in link:
        return "instagram"
    elif "tiktok.com" in link:
        return "tiktok"
    elif "youtube.com" in link or "youtu.be" in link:
        return "youtube"
    elif "telegram.me" in link or "t.me" in link:
        return "telegram"
    elif "twitter.com" in link or "x.com" in link:
        return "twitter"
    elif "vk.com" in link:
        return "vk"
    elif "ok.ru" in link:
        return "ok"
    elif "linkedin.com" in link:
        return "linkedin"
    elif "reddit.com" in link:
        return "reddit"
    elif "snapchat.com" in link:
        return "snapchat"
    elif "pinterest.com" in link:
        return "pinterest"
    elif "tumblr.com" in link:
        return "tumblr"
    elif "threads.net" in link:
        return "threads"
    elif "weibo.com" in link:
        return "weibo"
    elif "wechat.com" in link:
        return "wechat"
    else:
        return "track"  # Noma'lum yoki boshqa

async def increment_social_network_stat(network: str):
    if not network:
        return
    async with AsyncSession(engine) as session:
        try:
            result = await session.execute(select(SocialNetworkStat))
            stats = result.scalar_one_or_none()

            if not stats:
                stats = SocialNetworkStat()
                session.add(stats)       # bu o'zgarishi shart emas, lekin await commit bo'lishi shart
                await session.flush()    # optional, lekin yaxshi amaliyot
                await session.commit()

            if hasattr(stats, network):
                setattr(stats, network, getattr(stats, network) + 1)
                await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"❌ increment_social_network_stat error: {e}")


