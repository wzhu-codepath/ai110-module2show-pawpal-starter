# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
  1. The design is composed of 4 classes: Owner, Pet, Task and Scheduler. Owner would store information about the owner. Pet class represents a pet and would maintain a list of tasks that needs to be done. The task represents a specific activity holding duration, priority, type and logic to detremine whether or not it is due on a certain day. The scheduler generates a daily care plan by prioritizing tasks based on priority and timing.
- What classes did you include, and what responsibilities did you assign to each?
  1. Owner, pet, task and Scheduler.
     1. Owner:
        1. Attributes: name, dailyTimeAval
        2. Methods: updateTimeAval
     2. Pet:
        1. Attributes: name, species, tasks
        2. Methods: addTask, getTasks
     3. Task
        1. Attributes: name, duration, priority, taskType
        2. Methods: isDueToday
     4. Scheduler:
        1. Attributes: owner,pet, schedule
        2. Methods: genDailyPlan, prioritizeTasks, explainPlan

- 3 Core actions
  1. Adding a pet, Scheduling walk and seeing tasks for the day.

**b. Design changes**

- Did your design change during implementation?
  1. Yes.
- If yes, describe at least one change and why you made it.
  1. Conflict warnings was not part of the original design but was added so the program doesnt crash when it sees a conflict.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  1. **Daily time availability**: The scheduler respects `owner.dailyTimeAval` as a hard constraint—tasks only get scheduled if the total time fits within available minutes. Lower-priority tasks are dropped if they exceed the time budget.
  2. **Task priority (1-5 scale)**: Higher-priority tasks are scheduled first. The scheduler sorts by priority descending.
  3. **Task duration**: Acts as a secondary sort key (shorter tasks preferred when priority is equal) and determines if a task fits within remaining time.
  4. **Task frequency**: Only tasks due today (based on their frequency rules—DAILY, WEEKLY, MONTHLY, AS_NEEDED) are considered for scheduling.
  5. **Scheduled time (HH:MM format)**: Optional constraint used to sort tasks chronologically and detect scheduling conflicts.

- How did you decide which constraints mattered most?
  1. **Time availability** was the most critical constraint because a busy owner can't do tasks they don't have time for—it's a hard limit.
  2. **Priority** came second because the scenario specified that owners have preferences about which tasks matter most (e.g., medication before playtime).
  3. **Duration** was the tiebreaker—if two tasks have the same priority, fitting the shorter one first maximizes the number of tasks that can be scheduled.
  4. **Frequency** determined eligibility; tasks not due today shouldn't be scheduled.
  5. **Scheduled time** was lower priority since it's optional and mainly used for clarity and conflict detection rather than filtering tasks.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  1. One tradeoff my scheduler made was choosing simplicity and readability over full scheduling accuracy. This tradeoff checked for full time matches and produce a clear readble warning.
- Why is that tradeoff reasonable for this scenario?
  1. It was reasonable as it kept the algorithm short and deterministic.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
  1. Design brainstorming, providing me with skeleton code, buildign a comprehensive test harness, and debugging issues. 
- What kinds of prompts or questions were most helpful?
  1. Prompts that provided the most context served the useful as the agent knew where to reference key points. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  1. When I was working on the README it suggested overrighting something I already had and needed.
- How did you evaluate or verify what the AI suggested?
  1. Ensure the output was reasonable for the purpose. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
  1. All functions with emphasis on sorting, recurrence and conflict detection.
- Why were these tests important?
  1. Testing all the edge cases that may exist

**b. Confidence**

- How confident are you that your scheduler works correctly?
  1. Fairly confident.
- What edge cases would you test next if you had more time?
  1. Time ranges

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  1. Building a simple scheduler. 

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  1. Implement robust scheduler to avoid conflicts.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
  1. AI is helpful in helping you provide reasonable solutions, but the solutions must be checked. 