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
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  1. One tradeoff my scheduler made was choosing simplicity and readability over full scheduling accuracy. This tradeoff checked for full time matches and produce a clear readble warning.
- Why is that tradeoff reasonable for this scenario?
  1. It was reasonable as it kept the algorithm short and deterministic.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
