from nonebot import *
import json
from random import randint
import asyncio

bot = get_bot()
fd = "./dorothy/plugins/rs_data/"  # 存档的绝对路径前缀，记得改成你自己的
with open(fd + 'rsdata.json') as f:
    data = json.load(f)
with open(fd + 'rsplayer.json') as f:
    player = json.load(f)


def save(data, file):
    with open(file, 'w') as f:
        json.dump(data, f)


# main part
@on_command('rs', aliases='禁言转盘', only_to_me=False)
async def spin(session: CommandSession):
    if session.ctx['message_type'] == 'private':
        msg = '此功能仅适用于群聊'
        session.finish(msg)

    else:
        user = str(session.ctx['user_id'])
        group = session.ctx['group_id']
        if user not in player:
            player[user] = {}
            if session.ctx.sender['card'] is not None:
                player[user]['nickname'] = session.ctx.sender['card']
            else:
                player[user]['nickname'] = session.ctx.sender['nickname']
            player[user]['win'] = 0
            player[user]['death'] = 0

        if data['curnum'] == 0:
            msg = '欢迎参与紧张刺激的禁言转盘活动，请输入要填入的子弹数目(最多6颗)'
            bullet = session.get('bullet', prompt=msg, at_sender=True)
            if bullet == '6':
                ans = session.get('ans', prompt="你认真的？(y/n)")
                if ans == 'y':
                    await bot.set_group_ban(group_id=group, user_id=int(user), duration=60)
                    data['curnum'] = int(bullet)-1
                    data['next'] = 0
                    await session.send("装填完毕")
                else:
                    session.finish("好吧.")
            elif '0' < bullet < '6':
                data['curnum'] = int(bullet)
                data['next'] = randint(0, 6 - data['curnum'])
                await session.send("装填完毕")
            else:
                session.finish("请输入正确的数目.")

        else:
            if data['next'] == 0:
                await session.send("很不幸...")
                await bot.set_group_ban(group_id=group, user_id=int(user), duration=60)
                player[user]['death'] += 1
                data['curnum'] -= 1
                data['next'] = randint(0, 6 - data['curnum'])
                if data['curnum'] == 0:
                    await session.send("感谢各位的参与，让我们看一下游戏结算:")
                    await asyncio.sleep(1)
                    msg = ''
                    for k, i in player.items():
                        msg += ("%s:\nwin: %s death: %s\n" % (i['nickname'], i['win'], i['death']))
                    player.clear()
                    await session.send(msg)
                else:
                    await session.send("欢迎下一位.还剩%d发" % data['curnum'])
            else:
                data['next'] -= 1
                msg = "你活了下来，下一位.还剩%d发" % data['curnum']
                player[user]['win'] += 1
                await session.send(msg)

        save(data, fd + 'rsdata.json')
        save(player, fd + 'rsplayer.json')


@spin.args_parser
async def _(session: CommandSession):
    if session.is_first_run and session.current_arg_text.strip():
        # 第一次运行，如果有参数，则设置给 question
        session.state['bullet'] = session.current_arg_text.strip()


@on_command('rd', only_to_me=False)
async def spin(session: CommandSession):
    if session.ctx['message_type'] == 'private':
        msg = '此功能仅适用于群聊'
        session.finish(msg)

    elif data['curnum'] == 0:
        session.finish("游戏未开始")

    else:
        data['curnum'] = 0
        data['next'] = 0
        player.clear()
        save(data, fd + 'rsdata.json')
        save(player, fd + 'rsplayer.json')
        session.finish("已取消")
