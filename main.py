from pawpal_system import Owner, Pet, Task, Scheduler, Frequency


def main():
    """Main script to demonstrate the PawPal scheduling system."""
    
    # Create an owner
    owner = Owner("Alice", dailyTimeAval=120)  # 120 minutes available per day
    
    # Create pets
    dog = Pet("Max", "Golden Retriever")
    cat = Pet("Whiskers", "Siamese Cat")
    
    # Add pets to owner
    owner.addPet(dog)
    owner.addPet(cat)
    
    # Create tasks for the dog
    walk_task = Task(
        name="Morning Walk",
        duration=45,
        priority=5,
        taskType="Exercise",
        frequency=Frequency.DAILY
    )
    
    feed_task = Task(
        name="Feeding",
        duration=10,
        priority=5,
        taskType="Feeding",
        frequency=Frequency.DAILY
    )
    
    play_task = Task(
        name="Playtime",
        duration=30,
        priority=4,
        taskType="Exercise",
        frequency=Frequency.DAILY
    )
    
    # Add tasks to dog
    dog.addTask(walk_task)
    dog.addTask(feed_task)
    dog.addTask(play_task)
    
    # Create tasks for the cat
    cat_feed_task = Task(
        name="Cat Feeding",
        duration=5,
        priority=5,
        taskType="Feeding",
        frequency=Frequency.DAILY
    )
    
    litter_task = Task(
        name="Litter Box Cleaning",
        duration=10,
        priority=4,
        taskType="Cleaning",
        frequency=Frequency.DAILY
    )
    
    groom_task = Task(
        name="Grooming",
        duration=15,
        priority=3,
        taskType="Care",
        frequency=Frequency.WEEKLY
    )
    
    # Add tasks to cat
    cat.addTask(cat_feed_task)
    cat.addTask(litter_task)
    cat.addTask(groom_task)
    
    # Create scheduler and generate daily plan
    scheduler = Scheduler(owner)
    scheduler.genDailyPlan()
    
    # Print today's schedule
    print("=" * 60)
    print("TODAY'S SCHEDULE")
    print("=" * 60)
    print(scheduler.explainPlan())
    print("=" * 60)


if __name__ == "__main__":
    main()
