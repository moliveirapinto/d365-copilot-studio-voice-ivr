"""Generates the node-by-node diagrams used in docs/ (PNG). Run: python make_diagrams.py"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images')
os.makedirs(OUT, exist_ok=True)
S = 2  # supersampling for crisp output

KIND = {  # kind: (header color, label)
    'start': ('#5c2d91', 'Trigger'),
    'message': ('#8764b8', 'Message'),
    'question': ('#0f6cbd', 'Question'),
    'variable': ('#69797e', 'Set variable'),
    'condition': ('#0078d4', 'Condition'),
    'connector': ('#107c10', 'Dataverse action'),
    'topic': ('#8764b8', 'Go to another topic'),
    'transfer': ('#038387', 'Transfer conversation'),
    'end': ('#c50f1f', 'End conversation'),
    'd365': ('#0b6a0b', 'Dynamics 365'),
    'phone': ('#d83b01', 'Phone'),
    'rule': ('#8a5a00', 'Routing'),
}


def font(size, bold=False):
    return ImageFont.truetype(r'C:\Windows\Fonts\segoeui%s.ttf' % ('b' if bold else ''), size * S)


class Canvas:
    def __init__(self, w, h, title=None, subtitle=None):
        self.w, self.h = w, h
        self.img = Image.new('RGB', (w * S, h * S), '#faf9f8')
        self.d = ImageDraw.Draw(self.img)
        if title:
            self.d.text((24 * S, 14 * S), title, font=font(20, True), fill='#201f1e')
        if subtitle:
            self.d.text((24 * S, 44 * S), subtitle, font=font(12), fill='#605e5c')

    def wrap(self, text, width_px, f):
        words, lines, cur = text.split(' '), [], ''
        for w in words:
            t = (cur + ' ' + w).strip()
            if f.getlength(t) <= width_px * S:
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
        return lines

    def card(self, cx, y, w, kind, title, lines=()):
        color, label = KIND[kind]
        f_t, f_b = font(12, True), font(11)
        body = []
        for ln in lines:
            body += self.wrap(ln, w - 24, f_b)
        h = 30 + 10 + 17 * len(body) + (6 if body else 0)
        x0 = cx - w // 2
        d = self.d
        d.rounded_rectangle([x0 * S, y * S, (x0 + w) * S, (y + h) * S], radius=8 * S, fill='white', outline='#c8c6c4', width=S)
        d.rounded_rectangle([x0 * S, y * S, (x0 + w) * S, (y + 30) * S], radius=8 * S, fill=color)
        d.rectangle([x0 * S, (y + 20) * S, (x0 + w) * S, (y + 30) * S], fill=color)
        d.text(((x0 + 12) * S, (y + 8) * S), label.upper(), font=font(9, True), fill='#e8e8e8')
        d.text(((x0 + w - 12) * S - f_t.getlength(title), (y + 6) * S), title, font=f_t, fill='white')
        yy = y + 38
        for ln in body:
            d.text(((x0 + 12) * S, yy * S), ln, font=f_b, fill='#323130')
            yy += 17
        return (x0, y, x0 + w, y + h)

    def arrow(self, pts, label=None, color='#605e5c', lx=6, ly=-4):
        d = self.d
        P = [(x * S, y * S) for x, y in pts]
        for a, b in zip(P[:-1], P[1:]):
            d.line([a, b], fill=color, width=2 * S)
        (x1, y1), (x2, y2) = P[-2], P[-1]
        ang = math.atan2(y2 - y1, x2 - x1)
        L = 9 * S
        d.polygon([(x2, y2), (x2 - L * math.cos(ang - 0.4), y2 - L * math.sin(ang - 0.4)),
                   (x2 - L * math.cos(ang + 0.4), y2 - L * math.sin(ang + 0.4))], fill=color)
        if label:
            mx, my = (pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2
            d.text(((mx + lx) * S, (my + ly) * S), label, font=font(11, True), fill=color)

    def down(self, a, b, label=None):
        ax, ay = (a[0] + a[2]) / 2, a[3]
        bx, by = (b[0] + b[2]) / 2, b[1]
        if abs(ax - bx) < 1:
            self.arrow([(ax, ay), (bx, by)], label)
        else:
            mid = (ay + by) / 2
            self.arrow([(ax, ay), (ax, mid), (bx, mid), (bx, by)], label)

    def tag(self, x, y, text, fill='#fff4ce', edge='#c19c00', color='#6e5500'):
        f = font(11, True)
        w = f.getlength(text) / S + 16
        self.d.rounded_rectangle([x * S, y * S, (x + w) * S, (y + 22) * S], radius=11 * S, fill=fill, outline=edge, width=S)
        self.d.text(((x + 8) * S, (y + 3) * S), text, font=f, fill=color)

    def save(self, name):
        self.img.save(os.path.join(OUT, name), optimize=True)
        print('wrote', name, self.img.size)


def architecture():
    c = Canvas(1180, 770, 'Sales and Support Voice IVR: end-to-end call flow',
               'Copilot Studio agent (IVR) in front, Dynamics 365 Contact Center behind it')
    W = 250
    caller = c.card(150, 90, W, 'phone', 'Caller', ['Dials your phone number', 'Hears: "Press 1 or say sales, press 2 or say support"'])
    ws = c.card(150, 210, W, 'd365', 'Voice workstream', ['Phone number is attached to the Voice channel', 'The IVR agent answers first'])
    bot = c.card(150, 330, W, 'start', 'Copilot Studio IVR agent', ['Main Menu collects 1/2 (keypad) or speech', 'Sets Global.QueueName = Sales or Support'])
    chk = c.card(150, 460, W, 'connector', 'Check hours', ['1. Look up the queue ID by name', '2. Ask D365: is the queue open right now?', '3. If closed, read the D365 voice message'])
    c.down(caller, ws)
    c.down(ws, bot)
    c.down(bot, chk)

    closed = c.card(560, 440, 300, 'message', 'CLOSED', ['Plays the D365 automated message', 'MessageReceivedOutsideOperationHoursAck_PhoneCall', 'Then asks "anything else?". Yes replays the menu, No says goodbye. The caller is not transferred.'])
    opn = c.card(560, 625, 300, 'transfer', 'OPEN', ['"Please hold while I connect you"', 'Transfer conversation to D365 and pass QueueName'])
    c.arrow([(275, 520), (330, 520), (330, 480), (410, 480)], 'closed', '#c50f1f', lx=-40, ly=-26)
    c.arrow([(275, 545), (330, 545), (330, 670), (410, 670)], 'open', '#107c10', lx=-40, ly=8)

    rule = c.card(960, 330, 340, 'rule', 'Routing rules: Route to Queue', ['QueueName == Sales -> Sales queue', 'QueueName == Support -> Support queue', 'Hit policy: first match. Fallback queue: Support'])
    sq = c.card(860, 480, 200, 'd365', 'Sales queue', ['Open Mon-Fri 8:00-12:00'])
    pq = c.card(1070, 480, 200, 'd365', 'Support queue', ['Open Mon-Fri 12:00-18:00'])
    rep = c.card(960, 590, 300, 'd365', 'Representative', ['Accepts the call in the Customer Service workspace'])
    c.arrow([(710, 670), (760, 670), (760, 395), (790, 395)], 'QueueName', '#107c10', lx=-78, ly=130)
    c.arrow([(900, 420 + 0), (860, 420 + 0), (860, 480)])
    c.arrow([(1020, 420), (1070, 420), (1070, 480)])
    c.arrow([(860, 545), (860, 570), (960, 570), (960, 590)])
    c.arrow([(1070, 545), (1070, 570), (960, 570)])
    c.tag(24, 730, 'The Dataverse connector (maker connection) is used only by the three lookups in Check Hours And Transfer. No flows, plugins or custom APIs.')
    c.save('01-architecture.png')


def conv_start_menu():
    c = Canvas(980, 810, 'Topics: Conversation Start, then Main Menu', 'cr_salesandsupportivr.topic.ConversationStart and cr_salesandsupportivr.topic.MainMenu')
    W = 330
    a = c.card(250, 90, W, 'start', 'Conversation Start', ['On conversation start: fires when the call is answered'])
    b = c.card(250, 190, W, 'message', 'Message', ['Speech and text: "Thank you for calling."'])
    t = c.card(250, 290, W, 'topic', 'Go to Main Menu', ['dialog: cr_salesandsupportivr.topic.MainMenu'])
    c.down(a, b)
    c.down(b, t)

    m0 = c.card(700, 90, W, 'start', 'Main Menu', ['Recognized intent (empty). Only started by Go-to-topic, never by what the caller says.'])
    v1 = c.card(700, 200, W, 'variable', 'Set variable (two)', ['Global.QueueName = ""', 'Global.QueueId = ""', 'Declares the global variables once so later steps can assign them.'])
    q = c.card(700, 340, W, 'question', 'Question: menu', ['Speech: "If you want to talk to sales, press 1 or say sales. If you want to talk to support, press 2 or say support."', 'Entity: closed list { Sales (keypad 1), Support (keypad 2) }', 'Interruptions: off'])
    cond = c.card(700, 530, W, 'condition', 'Condition', ['MenuChoice = Sales ?', 'MenuChoice = Support ?', 'else: invalid or no answer'])
    c.down(m0, v1)
    c.down(v1, q)
    c.down(q, cond)
    s1 = c.card(540, 660, 250, 'variable', 'Sales branch', ['Global.QueueName = "Sales"', 'Go to Check Hours And Transfer'])
    s2 = c.card(830, 660, 250, 'variable', 'Support branch', ['Global.QueueName = "Support"', 'Go to Check Hours And Transfer'])
    c.arrow([(660, 627), (660, 643), (540, 643), (540, 660)])
    c.arrow([(740, 627), (740, 643), (830, 643), (830, 660)])
    c.tag(24, 765, 'else: "Sorry, I didn\'t get a valid selection" then Go to step: Question (the menu is read again)', '#fde7e9', '#c50f1f', '#750b1c')
    c.save('02-conversation-start-and-main-menu.png')


def check_hours():
    c = Canvas(1260, 1540, 'Topic: Check Hours And Transfer', 'cr_salesandsupportivr.topic.CheckHoursAndTransfer. All three Dataverse actions use the maker connection, so callers never sign in.')
    W = 430
    cx = 330
    n0 = c.card(cx, 80, W, 'start', 'Check Hours And Transfer', ['Recognized intent (empty). Started from Main Menu.'])
    n1 = c.card(cx, 160, W, 'variable', 'Set variable', ['Topic.QueueClosed = false. Safe default: if the queue cannot be found, the call is transferred and D365 decides.'])
    n2 = c.card(cx, 258, W, 'connector', 'List rows: look up queue ID', ['Table: queues', 'FetchXML: queue where name = Global.QueueName, top 1', 'Output: Topic.QueueLookup'])
    n3 = c.card(cx, 392, W, 'variable', 'Set variable', ['Global.QueueId = Coalesce(Text(First(QueueLookup.value).queueid), "")'])
    n4 = c.card(cx, 478, W, 'condition', 'Condition', ['Global.QueueId <> ""   (the queue was found)'])
    n5 = c.card(cx, 568, W, 'connector', 'Perform an unbound action', ['Action: msdyn_ExpandOperatingHoursForEntityCollection', 'msdyn_Start = Now()', 'msdyn_End = Now() + 1 minute', 'msdyn_EntityCollection = [ queue(Global.QueueId) ]', 'Returns the available slots for that minute'])
    n6 = c.card(cx, 742, W, 'variable', 'Set variable', ['Topic.QueueClosed = IsBlank(Find("Available", HoursResponse.msdyn_Result))', 'No "Available" slot in the next minute means closed'])
    n7 = c.card(cx, 850, W, 'condition', 'Condition', ['Topic.QueueClosed = true'])
    c.down(n0, n1)
    c.down(n1, n2)
    c.down(n2, n3)
    c.down(n3, n4)
    c.down(n4, n5, 'found')
    c.down(n5, n6)
    c.down(n6, n7)
    rx = n4[2]
    c.arrow([(rx, 520), (rx + 20, 520), (rx + 20, 826), (cx + 60, 826), (cx + 60, 850)], None, '#605e5c')
    c.tag(rx + 36, 560, 'not found: skip the hours check', '#f3f2f1', '#c8c6c4', '#605e5c')

    X = 930
    c1 = c.card(X, 790, 340, 'connector', 'CLOSED: List rows: voice message', ['Table: msdyn_ocsystemmessages', 'Row: MessageReceivedOutsideOperationHoursAck_PhoneCall', 'Reads msdyn_messagetext'])
    c2 = c.card(X, 930, 340, 'variable', 'Set variable', ['Topic.OohMessage = the D365 message, or a built-in fallback sentence'])
    c3 = c.card(X, 1016, 340, 'message', 'Message', ['Speech and text: {Topic.OohMessage}'])
    c4 = c.card(X, 1102, 340, 'question', 'Question: anything else?', ['"Is there anything else I can help you with? Press 1 or say yes, press 2 or say no."', 'Closed list: Yes (keypad 1), No (keypad 2)'])
    c5 = c.card(X, 1248, 340, 'condition', 'Condition', ['AnythingElse = Yes  ->  Go to Main Menu (the menu is played again)', 'else (No)  ->  continue below'])
    c6 = c.card(X, 1360, 340, 'message', 'Message', ['"Thank you for calling. Goodbye."'])
    c7 = c.card(X, 1440, 340, 'end', 'End conversation', ['The call ends only after the caller says no. Nobody is transferred.'])
    c.down(c1, c2)
    c.down(c2, c3)
    c.down(c3, c4)
    c.down(c4, c5)
    c.down(c5, c6)
    c.down(c6, c7)
    c.arrow([(n7[2], 868), (n7[2] + 45, 868), (n7[2] + 45, 830), (X - 170, 830)], None, '#c50f1f')
    c.tag(n7[2] + 55, 876, 'yes: closed', '#fde7e9', '#c50f1f', '#750b1c')

    d1 = c.card(cx, 950, W, 'message', 'OPEN: Message', ['"Please hold while I connect you."  (conversation outcome: Escalated)'])
    d2 = c.card(cx, 1040, W, 'transfer', 'Transfer conversation', ['Transfer type: Transfer to agent', 'Message to agent: "IVR selection - {Global.QueueName}"', 'Context: automatic. Passes Global.QueueName to D365.'])
    c.down(n7, d1)
    c.down(d1, d2)
    c.tag(cx + 10, 926, 'no: open', '#dff6dd', '#107c10', '#0b4f0b')
    c.save('03-check-hours-and-transfer.png')


def voice_topics():
    c = Canvas(1180, 330, 'Supporting voice topics', 'System topics tuned for a phone call')
    W = 255
    items = [
        ('Silence detection', ['Trigger: the caller is silent', 'Question: "Are you still there?"', 'Still no answer: "We\'re not detecting any activity. Please call back when it is convenient for you." and the topic ends.']),
        ('Speech unrecognized', ['Trigger: speech could not be understood', '"Sorry, I didn\'t catch that. Please try again."']),
        ('Unknown dial pad press', ['Trigger: a key that is not mapped, for example 3', '"Sorry, that is not a valid option. Please try again."']),
        ('Escalate', ['Trigger: "talk to a person", "customer service" and similar', 'Says "Let me connect you with the right team", then goes to Main Menu so the hours check and queue routing are never skipped.']),
    ]
    for i, (t, ls) in enumerate(items):
        c.card(24 + W // 2 + i * (W + 20), 80, W, 'start', t, ls)
    c.tag(24, 290, 'Template topics kept as shipped: Greeting, Goodbye, Thank you, Start over, Reset conversation, Fallback, Multiple topics matched, Sign in, End of conversation, Session timeout.')
    c.save('04-supporting-voice-topics.png')


def d365_setup():
    c = Canvas(1240, 600, 'Dynamics 365 setup created by scripts/Install-D365Setup.ps1', 'Every item uses a built-in Dataverse action, except the routing conditions, which are written into the ruleset definition')
    W = 270
    h1 = c.card(170, 90, W, 'd365', 'Operating hours: Sales', ['Mon-Fri 08:00-12:00', 'msdyn_CreateOperatingHours'])
    h2 = c.card(170, 200, W, 'd365', 'Operating hours: Support', ['Mon-Fri 12:00-18:00', 'msdyn_CreateOperatingHours'])
    q1 = c.card(520, 90, W, 'd365', 'Queue: Sales (voice)', ['Operating hours attached', 'msdyn_ManageQueue: Create, SetOperatingHours'])
    q2 = c.card(520, 200, W, 'd365', 'Queue: Support (voice)', ['Operating hours attached', 'Also the workstream fallback queue'])
    c.arrow([(305, 125), (385, 125)])
    c.arrow([(305, 235), (385, 235)])
    cp = c.card(520, 330, W, 'd365', 'Capacity profile', ['"Voice IVR inbound": 1 work item', 'Voice requires exactly 1'])
    ws = c.card(930, 90, 330, 'd365', 'Voice IVR Workstream', ['Channel: Voice (phone number added later)', 'Push distribution, profile-based capacity', 'Copilot agent: Sales and Support IVR', 'Default queue: Support'])
    cv = c.card(930, 270, 330, 'rule', 'Context variable: QueueName', ['Text. Filled by the agent during the transfer'])
    rs = c.card(930, 370, 330, 'rule', 'Ruleset: Route to Queue', ['Hit policy: first', 'QueueName == Sales -> Sales queue', 'QueueName == Support -> Support queue'])
    c.arrow([(655, 365), (720, 365), (720, 150), (765, 150)])
    c.arrow([(930, 215), (930, 270)], 'has')
    c.arrow([(930, 335), (930, 370)], 'used in conditions')
    c.arrow([(765, 430), (690, 430), (690, 270), (655, 270)], None, '#605e5c')
    c.arrow([(690, 430), (690, 140), (655, 140)], None, '#605e5c')
    c.tag(24, 550, 'Not created (needs your phone number): the Voice channel on the workstream.')
    c.save('05-d365-setup.png')


if __name__ == '__main__':
    architecture()
    conv_start_menu()
    check_hours()
    voice_topics()
    d365_setup()
