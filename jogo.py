import time
import sys
import pygame
import math
import random
from pygame.locals import *

#friction = 0.0039
friction = 0.025
k = 0.75
mouseX = 0
mouseY = 0

# same as arduino's map function
def scale(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def getDistance(x1, y1, x2, y2):
    xDistance = x2 - x1
    yDistance = y2 - y1
    return math.sqrt(math.pow(xDistance, 2) + math.pow(yDistance, 2))

class Player:
    def __init__(self, name, team, x, y, color):
        self.name = name
        self.team = team
        self.x = x
        self.y = y
        self.initialX = x
        self.initialY = y
        self.borderWidth = 4
        self.radius = 30
        self.borderColor = (0, 0, 0)
        self.vx = 0
        self.vy = 0
        self.hover = False
        self.color = color
        self.textColor = (255, 255, 255)
        self.textBackgroundColor = self.color
        self.drawVector = False
        self.applyForce = False

    def update(self):
        if self.drawVector:
            self.drawForceVector()
        self.draw()
        self.move()
        self.collisionEdges()
        self.collisionPlayers()
        self.drawVelocityVectors()
        self.collisionBall()
        self.collisionGoalposts()

    def draw(self):
        if self.hover:
            self.borderColor = (255, 255, 255)
        else:
            self.borderColor = (0, 0, 0)
        # border
        pygame.draw.circle(win, self.borderColor, (self.x, self.y), self.radius)

        # circle
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius - self.borderWidth)
        # text
        font = pygame.font.Font(None, 50)
        text = font.render(self.name, True, self.textColor, self.textBackgroundColor)
        win.blit(text, [self.x - self.radius / 3.5, self.y - self.radius / 2])

    def move(self):
        if self.vx != 0:
            self.vx *= 1 - friction
            self.x += int(self.vx)

        if self.vy != 0:
            self.vy *= 1 - friction
            self.y += int(self.vy)

    def collisionEdges(self):
        # top
        if self.y - self.radius <= pitchTop:
            self.vy *= k
            self.vy = -self.vy
            self.y = pitchTop + self.radius

        # bottom
        if self.y + self.radius >= pitchBottom:
            self.vy *= k
            self.vy = -self.vy
            self.y = pitchBottom - self.radius
        
        # right
        if self.x + self.radius >= pitchRight and (self.y < goalpostRight1[1] or self.y > goalpostRight2[1]):
            self.vx *= k
            self.vx = -self.vx
            self.x = pitchRight - self.radius
        
        # left
        if self.x - self.radius <= pitchLeft and (self.y < goalpostLeft1[1] or self.y > goalpostLeft2[1]):
            self.vx *= k
            self.vx = -self.vx
            self.x = pitchLeft + self.radius

        # goalpostLeft top border
        if self.y - self.radius <= 297 and self.x < goalpostLeft1[0]:
            self.vy *= k
            self.vy = -self.vy
            self.y = 297 + self.radius
        
        # goalpostLeft bottom border
        if self.y + self.radius >= 513 and self.x < goalpostLeft1[0]:
            self.vy *= k
            self.vy = -self.vy
            self.y = 513 - self.radius
        
        # goalpostLeft left border
        if self.x - self.radius <= 145:
            self.vx *= k
            self.vx = -self.vx
            self.x = 145 + self.radius

        # goalpostRight top border
        if self.y - self.radius <= 297 and self.x > goalpostRight1[0]:
            self.vy *= k
            self.vy = -self.vy
            self.y = 297 + self.radius

        # goalpostRight bottom border
        if self.y + self.radius >= 513 and self.x > goalpostRight1[0]:
            self.vy *= k
            self.vy = -self.vy
            self.y = 513 - self.radius

        # goalpostLeft right border
        if self.x + self.radius >= 1615:
            self.vx *= k
            self.vx = -self.vx
            self.x = 1615 - self.radius


    def drawForceVector(self):
        force = getDistance(self.x, self.y, mouseX, mouseY)
        lineColor = (scale(force, 0, 500, 0, 255), scale(force, 0, 500, 255, 0), 0)
        try:
            pygame.draw.line(win, lineColor, (self.x, self.y), (mouseX, mouseY), 5)
        except:
            pygame.draw.line(win, (255, 0, 0), (self.x, self.y), (mouseX, mouseY), 5)
        if force > 500:
            force = 500
        if self.applyForce:
            self.applyForce = False
            self.drawVector = False
            velocity = scale(force, 0, 500, 0, 50)
            angle = getAngle(mouseX, mouseY, self.x, self.y)
            self.vx = velocity * math.cos(angle)
            self.vy = velocity * math.sin(angle)
    
    def getIndex(self):
        for i in range(0, len(players) - 1):
            if players[i].name == self.name and players[i].team == self.team:
                return i

    def collisionPlayers(self):
        for player in players:
            if getDistance(self.x, self.y, player.x, player.y) < (self.radius + player.radius) and player != self:
                resolveCollision(self, player)
                
    
    def drawVelocityVectors(self):
        # vx
        pygame.draw.line(win, (255, 0, 0), (self.x, self.y), (self.x + self.vx * self.radius, self.y), 2)
        # vy
        pygame.draw.line(win, (0, 255, 0), (self.x, self.y), (self.x, self.y + self.vy * self.radius), 2)
        # v
        pygame.draw.line(win, (0, 0, 255), (self.x, self.y), (self.x + self.vx * self.radius, self.y + self.vy * self.radius), 2)

    def collisionBall(self):
        for player in players:
            if getDistance(self.x, self.y, ball.x, ball.y) < (self.radius + ball.radius) and player != self:
                resolveCollision(self, ball)
    
    def collisionGoalposts(self):
        for goalpost in goalposts:
            if getDistance(self.x, self.y, goalpost.x, goalpost.y) < (self.radius + goalpost.radius):
                resolveCollision(self, goalpost)

    def resetPosition(self):
        self.x = self.initialX
        self.y = self.initialY
        self.vx = 0
        self.vy = 0
        

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.initialX = x
        self.initialY = y
        self.radius = 25
        self.vx = 0
        self.vy = 0

    def update(self):
        self.draw()
        self.move()
        self.collisionEdges()
        self.collisionGoalposts()
        self.checkGoal()
        self.drawVelocityVectors()

    def draw(self):
        # circle
        win.blit(ballImage, (self.x - self.radius, self.y - self.radius))
    
    def move(self):
        if self.vx != 0:
            self.vx *= 1 - friction
            self.x += int(self.vx)

        if self.vy != 0:
            self.vy *= 1 - friction
            self.y += int(self.vy)

    def collisionEdges(self):
        # top
        if self.y - self.radius <= pitchTop:
            self.vy *= k
            self.vy = -self.vy
            self.y = pitchTop + self.radius

        # bottom
        if self.y + self.radius >= pitchBottom:
            self.vy *= k
            self.vy = -self.vy
            self.y = pitchBottom - self.radius
        
        # right
        if self.x + self.radius >= pitchRight and (self.y < goalpostRight1[1] or self.y > goalpostRight2[1]):
            self.vx *= k
            self.vx = -self.vx
            self.x = pitchRight - self.radius
        
        # left
        if self.x - self.radius <= pitchLeft and (self.y < goalpostLeft1[1] or self.y > goalpostLeft2[1]):
            self.vx *= k
            self.vx = -self.vx
            self.x = pitchLeft + self.radius

        # goalpostLeft top border
        if self.y - self.radius <= 297 and self.x < goalpostLeft1[0]:
            self.vy *= k
            self.vy = -self.vy
            self.y = 297 + self.radius
        
        # goalpostLeft bottom border
        if self.y + self.radius >= 513 and self.x < goalpostLeft1[0]:
            self.vy *= k
            self.vy = -self.vy
            self.y = 513 - self.radius
        
        # goalpostLeft left border
        if self.x - self.radius <= 145:
            self.vx *= k
            self.vx = -self.vx
            self.x = 145 + self.radius

        # goalpostRight top border
        if self.y - self.radius <= 297 and self.x > goalpostRight1[0]:
            self.vy *= k
            self.vy = -self.vy
            self.y = 297 + self.radius

        # goalpostRight bottom border
        if self.y + self.radius >= 513 and self.x > goalpostRight1[0]:
            self.vy *= k
            self.vy = -self.vy
            self.y = 513 - self.radius

        # goalpostLeft right border
        if self.x + self.radius >= 1615:
            self.vx *= k
            self.vx = -self.vx
            self.x = 1615 - self.radius

    def collisionGoalposts(self):
        for goalpost in goalposts:
            if getDistance(self.x, self.y, goalpost.x, goalpost.y) < (self.radius + goalpost.radius + 2):
                goalpost.vx = 0
                goalpost.vy = 0
                resolveCollision(self, goalpost)

    def resetPosition(self):
        self.x = self.initialX
        self.y = self.initialY
        self.vx = 0
        self.vy = 0

    def checkGoal(self):
        if self.x + self.radius <= 240:
            ball.x = self.initialX
            ball.y = self.initialY
            scoreboard.incrementGoal(2)
            self.resetPosition()

            # play sound
            pygame.mixer.music.load('sounds/goal.mp3')
            pygame.mixer.music.play(0)

            for player in players:
                player.resetPosition()

        if self.x - self.radius >= 1520:
            ball.x = self.initialX
            ball.y = self.initialY
            scoreboard.incrementGoal(1)
            self.resetPosition()

            # play sound
            pygame.mixer.music.load('sounds/goal.mp3')
            pygame.mixer.music.play(0)

            for player in players:
                player.resetPosition()
    
    def drawVelocityVectors(self):
        # vx
        pygame.draw.line(win, (255, 0, 0), (self.x, self.y), (self.x + self.vx * self.radius, self.y), 2)
        # vy
        pygame.draw.line(win, (0, 255, 0), (self.x, self.y), (self.x, self.y + self.vy * self.radius), 2)
        # v
        pygame.draw.line(win, (0, 0, 255), (self.x, self.y), (self.x + self.vx * self.radius, self.y + self.vy * self.radius), 2)

class Scoreboard:
    def __init__(self, team1Score, team2Score):
        self.team1Score = team1Score
        self.team2Score = team2Score

    def draw(self):
        #draw scoreboard
        middleX = int(winWidth / 2)
        scoreboardWidth = 500
        scoreboardHeight = 60
        backgroundColor = (0, 175, 0)
        
        # border
        pygame.draw.rect(win, (0, 0, 0), (middleX - scoreboardWidth / 2, 20, scoreboardWidth, scoreboardHeight), 5)
        # rectangle
        pygame.draw.rect(win, backgroundColor, (middleX - scoreboardWidth / 2, 20, scoreboardWidth, scoreboardHeight))

        # result
        result = f"Blue Team {str(self.team1Score)} v {str(self.team2Score)} Red Team"
        font = pygame.font.Font(None, 50)
        text = font.render(result, True, (255, 255, 255), backgroundColor)
        win.blit(text, [middleX - 220, 30])

    def incrementGoal(self, scoringTeam):
        if scoringTeam == 1:
            self.team1Score += 1
        
        if scoringTeam == 2:
            self.team2Score += 1


class Goalpost:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.radius = 16
        self.color = color
        self.vx = 0
        self.vy = 0
    def draw(self):
        pygame.draw.circle(win, (0, 0, 0), (self.x, self.y), self.radius)
        pygame.draw.circle(win, self.color, (self.x, self.y), 12)

def atLeastOneVector():
    result = False
    for player in players:
        if player.drawVector:
            result = True
    return result

def getAngle(x1, y1, x2, y2):
    xDistance = x2 - x1
    yDistance = y2 - y1
    return math.atan2(yDistance, xDistance)

def resolveCollision(player, otherPlayer):
    collisionAngle = getAngle(player.x, player.y, otherPlayer.x, otherPlayer.y)
    # angles
    if math.fabs(collisionAngle) < 10 * math.pi / 180:
        thetha1 = collisionAngle - math.pi
    elif math.fabs(collisionAngle) < math.pi + 10 * math.pi / 180:
        thetha1 = collisionAngle - math.pi
    else:
        thetha1 = collisionAngle + math.pi / 2

    thetha2 = collisionAngle

    # initial velocity
    u1 = math.sqrt(player.vx * player.vx + player.vy * player.vy)
    u2 = math.sqrt(otherPlayer.vx * otherPlayer.vx + otherPlayer.vy * otherPlayer.vy)

    # coefficient of restitution
    e = 0.1

    # final velocity
    v1 = (e * (u2 - u1) + u1 + u2) / 2
    v2 = (e * (u1 - u2) + u1 + u2) / 2

    # calculate x and y component of v1
    v1x = v1 * math.cos(thetha1)
    v1y = v1 * math.sin(thetha1)

    # calculate x and y component of v2
    v2x = v2 * math.cos(thetha2)
    v2y = v2 * math.sin(thetha2)

    # change final velocities
    player.vx = v1x
    player.vy = v1y

    otherPlayer.vx = v2x
    otherPlayer.vy = v2y

pygame.init()

# iniciar windows de jogo
winWidth = 1760
winHeight = 774

pygame.display.set_caption("Game")
pygame.display.set_icon(pygame.image.load("img/ball.png"))

centerY = int(winHeight / 2) + 18

win = pygame.display.set_mode((winWidth, winHeight))
pygame.display.update()

# field background image
field = pygame.image.load("img/field.png").convert()

players = []

pitchTop = 116
pitchBottom = 693
pitchLeft = 247
pitchRight = 1514

marginTopBottom = 50
marginLeftRight = 100

spaceBetweenYColumn1 = int((pitchBottom - pitchTop - marginTopBottom * 2) / 5)
spaceBetweenYColumn2 = int((pitchBottom - pitchTop - marginTopBottom * 2) / 2)
spaceBetweenYColumn3 = int((pitchBottom - pitchTop - marginTopBottom * 2))
spaceBetweenX = int(((winWidth / 2) - pitchLeft) / 6 + pitchTop)

# team 1 formation 2-2-1
# 2
#players.append(Player("1", 1, spaceBetweenX + marginLeftRight + 50, spaceBetweenYColumn1 * 1 + pitchTop, (0, 0, 150)))
players.append(Player("1", 1, spaceBetweenX + marginLeftRight, spaceBetweenYColumn1 * 2 + pitchTop, (0, 0, 150)))
#players.append(Player("3", 1, spaceBetweenX + marginLeftRight, spaceBetweenYColumn1 * 3 + pitchTop, (0, 0, 150)))
players.append(Player("2", 1, spaceBetweenX + marginLeftRight, spaceBetweenYColumn1 * 4 + pitchTop, (0, 0, 150)))
#players.append(Player("5", 1, spaceBetweenX + marginLeftRight + 50, spaceBetweenYColumn1 * 5 + pitchTop, (0, 0, 150)))
# 2
players.append(Player("3", 1, spaceBetweenX * 2 + marginLeftRight, spaceBetweenYColumn2 * 1 + marginTopBottom, (0, 0, 150)))
players.append(Player("4", 1, spaceBetweenX * 2 + marginLeftRight, spaceBetweenYColumn2 * 2 + marginTopBottom, (0, 0, 150)))
# 1
players.append(Player("5", 1, int(spaceBetweenX * 2.5) + marginLeftRight, centerY, (0, 0, 150)))

#team 2 formation 2-2-1
# 2
#players.append(Player("1", 2, pitchRight - spaceBetweenX + marginLeftRight - 50, spaceBetweenYColumn1 * 1 + pitchTop, (215, 0, 0)))
players.append(Player("1", 2, pitchRight - spaceBetweenX + marginLeftRight, spaceBetweenYColumn1 * 2 + pitchTop, (215, 0, 0)))
#players.append(Player("3", 2, pitchRight - spaceBetweenX + marginLeftRight, spaceBetweenYColumn1 * 3 + pitchTop, (215, 0, 0)))
players.append(Player("2", 2, pitchRight - spaceBetweenX + marginLeftRight, spaceBetweenYColumn1 * 4 + pitchTop, (215, 0, 0)))
#players.append(Player("5", 2, pitchRight - spaceBetweenX + marginLeftRight - 50, spaceBetweenYColumn1 * 5 + pitchTop, (215, 0, 0)))
# 2
players.append(Player("3", 2, pitchRight - spaceBetweenX * 2 + marginLeftRight, spaceBetweenYColumn2 * 1 + marginTopBottom, (215, 0, 0)))
players.append(Player("4", 2, pitchRight - spaceBetweenX * 2 + marginLeftRight, spaceBetweenYColumn2 * 2 + marginTopBottom, (215, 0, 0)))
# 1
players.append(Player("5", 2, pitchRight - int(spaceBetweenX * 2.5) + marginLeftRight, centerY, (215, 0, 0)))


# ball image
ballImage = pygame.image.load("img/ball.png")
ballImage = pygame.transform.scale(ballImage, (50, 50))
ball = Ball(int(winWidth / 2), centerY)

scoreboard = Scoreboard(0, 0)

goalposts = []

# left goalposts
goalpostLeft1 = (244, 294)
goalpostLeft2 = (244, 514)

goalposts.append(Goalpost(goalpostLeft1[0], goalpostLeft1[1], (0, 0, 150)))
goalposts.append(Goalpost(goalpostLeft2[0], goalpostLeft2[1], (0, 0, 150)))

# right goalposts
goalpostRight1 = (1517, 294)
goalpostRight2 = (1517, 514)

goalposts.append(Goalpost(goalpostRight1[0], goalpostRight1[1], (215, 0, 0)))
goalposts.append(Goalpost(goalpostRight2[0], goalpostRight2[1], (215, 0, 0)))


turn = 1
moves = 0

count = 0

while True:
    win.blit(field, (0, 0))
    # draw scoreboard
    scoreboard.draw()
    
    # update players
    for player in players:
        player.update()

    # update ball
    ball.update()

    # draw posts
    for goalpost in goalposts:
        goalpost.draw()

    # listen to events
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # e.button == 1 (left mouse click)
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and not atLeastOneVector():
            mouseX, mouseY = pygame.mouse.get_pos()
            for player in players:
                if player.hover:
                    player.drawVector = True
                    count = 1
        
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and atLeastOneVector() and count == 2:
            for player in players:
                if player.drawVector:
                    player.applyForce = True
                    turn = 1 if turn == 2 else 2

        if e.type == pygame.KEYDOWN and e.key == K_ESCAPE and atLeastOneVector() and count == 2:
            for player in players:
                if player.drawVector:
                    player.drawVector = False

        if e.type == pygame.MOUSEMOTION:
            mouseX, mouseY = pygame.mouse.get_pos()
            for player in players:
                if player.team == turn and getDistance(mouseX, mouseY, player.x, player.y) <= player.radius and not atLeastOneVector():
                    player.hover = True
                elif player.drawVector == False:
                    player.hover = False

    pygame.display.flip()

    if count == 1:
        count = 2

pygame.quit()