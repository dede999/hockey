# Hockey Django

> Suddenly I had the idea of improving my Django skills
> with something I love: Hockey. There's a chance I can 
> use this  project as a template no matter what sport 



## 1- Simulating games

#### 1.1 - What I wanna do? (general plan)

* **Neutral Zone** (rink = 0)
	* puck may remain on neutral zone (_no momentum change_)
	* puck may go to some offensive area (_little momentum change_)
* **Offensive Zone** (rink = +/-1)
	* Goal H (_big momentum gain_)
	* Goal Attempt
	* Puck gets cleared

#### 1.2 - Intermediary Plan

* Each period has 40 turns (**2 turns / minute**)
    * Both teams will have a offensive attempt
* During a an offensive turn, some events may occur
    * A goal 
        * _attacking team gains momentum_
    * A goal attempt
        * _defending team gains momentum_