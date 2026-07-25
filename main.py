import asyncio
import random
from highrise import BaseBot, User, Position, AnchorPosition
from highrise.models import SessionMetadata

# ---------------------------------------------------------
# 🔑 بيانات البوت الجاهزة
# ---------------------------------------------------------
ROOM_ID = "67843fa0682e85c69a2390b0"
BOT_TOKEN = "F16e5c1e5904c3e76e4fe068d3f3a6b65cc10ec2639923804dc4d86d0798fcf1"
# ---------------------------------------------------------

# قائمة لمتابعة اللاعبين اللي بيتم طيرانهم حالياً
FLYING_USERS = set()

# قاموس الرقصات (من 1 لـ 200)
DANCE_MAP = {
    "1": "dance-ghost",         # Ghost (الشبح)
    "2": "dance-wrist",         # Wrist (ريست)
    "3": "emote-float",         # Float (الطيران)
    "4": "emote-pose10",        # Cute Pose
    "5": "dance-floss",         # Floss
    "6": "dance-sexy",          # Sexy Dance
    "7": "dance-shoppingcart",  # Shopping Cart
    "8": "dance-macarena",      # Macarena
    "9": "dance-weird",         # Weird Dance
    "10": "dance-tiktok2",      # TikTok 2
}

# لتغطية باقي الأرقام حتى 200 تلقائياً
DEFAULT_EMOTES = [
    "dance-ghost", "dance-wrist", "emote-float", "dance-floss", 
    "dance-sexy", "dance-shoppingcart", "dance-macarena", "dance-weird",
    "dance-tiktok2", "dance-tiktok8", "dance-duckwalk", "dance-pennywise"
]

for i in range(11, 201):
    DANCE_MAP[str(i)] = DEFAULT_EMOTES[i % len(DEFAULT_EMOTES)]


class HighriseBot(BaseBot):
    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("✅ Highrise Bot is ONLINE with Swing & Teleport Commands!")

    # الترحيب باللاعبين عند الدخول
    async def on_user_join(self, user: User, position: Position | AnchorPosition) -> None:
        try:
            await self.highrise.chat(f"منور يا {user.username}! ✨ رقص (1-200) | اسحب @اسم | مرجح @اسم | وقف @اسم 🚀")
        except Exception as e:
            print(f"Error on join: {e}")

    # وظيفة الطيران/المرجحة المستمرة
    async def swing_user(self, target_user: User):
        FLYING_USERS.add(target_user.id)
        await self.highrise.chat(f"طياررررران! 🚀 طيرنا @{target_user.username} في الغرفة!")
        
        while target_user.id in FLYING_USERS:
            # توليد إحداثيات عشوائية جوه الغرفة مع ارتفاعات مختلفة
            rx = random.uniform(1.0, 14.0)
            ry = random.uniform(2.0, 15.0)
            rz = random.uniform(1.0, 14.0)
            try:
                await self.highrise.teleport(target_user.id, Position(rx, ry, rz))
                await asyncio.sleep(0.5) # السرعة بين كل نطّة والتانية
            except Exception:
                break

    # أوامر الشات
    async def on_chat(self, user: User, message: str) -> None:
        msg = message.strip()
        msg_lower = msg.lower()

        # --- أمر المرجحة / الطيران (مرجح @اسم_اللاعب) ---
        if msg_lower.startswith("مرجح ") or msg_lower.startswith("طير "):
            parts = msg.split()
            if len(parts) >= 2:
                target_username = parts[1].replace("@", "").strip()
                room_users = (await self.highrise.get_room_users()).content
                target_user = next((u for u, _ in room_users if u.username.lower() == target_username.lower()), None)

                if target_user:
                    if target_user.id not in FLYING_USERS:
                        asyncio.create_task(self.swing_user(target_user))
                    else:
                        await self.highrise.chat(f"اللاعب @{target_user.username} بيمرجح بالفعل! 🌀")
                else:
                    await self.highrise.chat(f"اللاعب @{target_username} مش موجود في الغرفة!")

        # --- أمر إيقاف المرجحة والتنزيل للأرض (وقف @اسم_اللاعب) ---
        elif msg_lower.startswith("وقف ") or msg_lower.startswith("نزل "):
            parts = msg.split()
            if len(parts) >= 2:
                target_username = parts[1].replace("@", "").strip()
                room_users = (await self.highrise.get_room_users()).content
                target_user = next((u for u, _ in room_users if u.username.lower() == target_username.lower()), None)

                if target_user:
                    if target_user.id in FLYING_USERS:
                        FLYING_USERS.remove(target_user.id)
                        await asyncio.sleep(0.6)
                        await self.highrise.teleport(target_user.id, Position(7.5, 0.0, 7.5))
                        await self.highrise.chat(f"تم إيقاف @{target_user.username} وتنزيله للأرض بسلام! 🛬✨")
                    else:
                        await self.highrise.chat(f"اللاعب @{target_user.username} مش طاير أصلاً!")
                else:
                    await self.highrise.chat(f"اللاعب @{target_username} مش موجود في الغرفة!")

        # --- خاصية السحب (اسحب @اسم_اللاعب) ---
        elif msg_lower.startswith("اسحب ") or msg_lower.startswith("سحب "):
            parts = msg.split()
            if len(parts) >= 2:
                target_username = parts[1].replace("@", "").strip()
                room_users = (await self.highrise.get_room_users()).content
                target_user = None
                caller_position = None

                for u, pos in room_users:
                    if u.username.lower() == target_username.lower():
                        target_user = u
                    if u.id == user.id:
                        caller_position = pos

                if target_user and caller_position:
                    if isinstance(caller_position, Position):
                        await self.highrise.teleport(target_user.id, Position(caller_position.x + 0.5, caller_position.y, caller_position.z))
                        await self.highrise.chat(f"تم سحب @{target_user.username} إلى @{user.username} 🧲✨")
                    else:
                        await self.highrise.chat("مش قادر أحدد موقعك بالظبط عشان أسحبه ليك!")
                elif not target_user:
                    await self.highrise.chat(f"اللاعب @{target_username} مش موجود في الغرفة!")

        # --- تشغيل الرقص بالأرقام ---
        elif msg_lower in DANCE_MAP:
            try:
                await self.highrise.send_emote(DANCE_MAP[msg_lower], user.id)
            except Exception as e:
                print(f"Emote error: {e}")

        # --- أمر الصعود للدور التاني ---
        elif msg_lower == "!up":
            await self.highrise.teleport(user.id, Position(7.5, 5.0, 7.5))
            await self.highrise.chat(f"تم نقلك للدور التاني يا {user.username} ⬆️")

        # --- أمر الصعود للدور الأخير (VIP) ---
        elif msg_lower in ["!vip", "!ivp"]:
            await self.highrise.teleport(user.id, Position(7.5, 15.0, 7.5))
            await self.highrise.chat(f"تم نقلك للدور الأخير (VIP) يا {user.username} 👑")

        # --- أمر النزول للأرض ---
        elif msg_lower == "!down":
            await self.highrise.teleport(user.id, Position(7.5, 0.0, 7.5))
            await self.highrise.chat(f"تم نزولك للأسفل يا {user.username} ⬇️")

        # --- أمر رقص الغرفة كلها ---
        elif msg_lower == "!danceall":
            room_users = (await self.highrise.get_room_users()).content
            for room_user, _ in room_users:
                await self.highrise.send_emote("dance-ghost", room_user.id)
            await self.highrise.chat("يلا كلنا جوست! 👻🔥")

if __name__ == "__main__":
    from highrise.__main__ import main
    import sys
    
    # تشغيل البوت باستخدام الـ Room ID والـ Token مباشرة
    sys.argv = ["highrise", "main:HighriseBot", ROOM_ID, BOT_TOKEN]
    main()
