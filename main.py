import csv
import random
from collections import defaultdict

# Constants
NUM_GROUPS = 5
NUM_SUBJECTS = 6
NUM_LECTURERS = 10
NUM_ROOMS = 10
STUDENTS_PER_GROUP = 16
SEMESTER_WEEKS = 14
DAYS_PER_WEEK = 4
PERIODS_PER_DAY = 3  # Three periods per day of 1.5 hours each

# Random Range Constants
LECTURE_HOURS_RANGE = (20, 30)  # Range for lecture hours per subject
PRACTICAL_HOURS_RANGE_WITH_SUBGROUPS = (10, 15)  # Range when subject requires subgroups
PRACTICAL_HOURS_RANGE_NO_SUBGROUPS = (10, 15)  # Range when subject does not require subgroups
LECTURER_SUBJECTS_RANGE = (1, 3)  # Range for number of subjects a lecturer can teach
ROOM_CAPACITY_RANGE = (40, 100)  # Range for room capacities
GROUP_SUBJECTS_RANGE = (6, 6)  # Range for number of subjects assigned to each group
SUBJECT_REQUIRES_SUBGROUPS_PROBABILITY = 0.5  # Probability that a subject requires subgroups

# Data Classes
class Group:
    def __init__(self, name, num_students):
        self.name = name
        self.num_students = num_students
        self.subgroups = [f"{name}_A", f"{name}_B"]
        self.subjects = {}  # Subject name mapped to SubjectAssignment

class SubjectAssignment:
    def __init__(self, subject, lecture_hours, practical_hours):
        self.subject = subject
        self.lecture_hours = lecture_hours
        self.practical_hours = practical_hours
        self.lecture_hours_scheduled = 0.0
        self.practical_hours_scheduled = 0.0

class Subject:
    def __init__(self, name, requires_subgroups):
        self.name = name
        self.requires_subgroups = requires_subgroups

class Lecturer:
    def __init__(self, name, can_teach_subjects, can_conduct):
        self.name = name
        self.can_teach_subjects = can_teach_subjects
        self.can_conduct = can_conduct

class Room:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity

class Scheduler:
    def __init__(self):
        self.groups = []
        self.subjects = []
        self.lecturers = []
        self.rooms = []
        self.schedule = defaultdict(list)  # Key: (Week, Day, PeriodIndex), Value: List of scheduled classes
        # Availability will be stored per time slot
        self.lecturer_availability = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(bool))))
        self.group_availability = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(bool))))
        self.room_availability = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(bool))))
        self.daily_periods = []  # Will hold periods for each day
        self.group_subject_assignments = defaultdict(dict)  # Group name -> subject name -> SubjectAssignment
        self.room_assignment_index = 0  # For round-robin room assignment

    def generate_groups(self):
        for i in range(1, NUM_GROUPS + 1):
            group_name = f"Group_{i}"
            group = Group(group_name, STUDENTS_PER_GROUP)
            self.groups.append(group)
        self.save_groups_to_csv()

    def generate_subjects(self):
        for i in range(1, NUM_SUBJECTS + 1):
            subject_name = f"Subject_{i}"
            requires_subgroups = random.random() < SUBJECT_REQUIRES_SUBGROUPS_PROBABILITY
            subject = Subject(subject_name, requires_subgroups)
            self.subjects.append(subject)
        self.save_subjects_to_csv()

    def assign_subjects_to_groups(self):
        for group in self.groups:
            num_subjects = random.randint(*GROUP_SUBJECTS_RANGE)
            assigned_subjects = random.sample(self.subjects, num_subjects)
            for subject in assigned_subjects:
                lecture_hours = random.randint(*LECTURE_HOURS_RANGE)
                if subject.requires_subgroups:
                    practical_hours = random.randint(*PRACTICAL_HOURS_RANGE_WITH_SUBGROUPS)
                else:
                    practical_hours = random.randint(*PRACTICAL_HOURS_RANGE_NO_SUBGROUPS)
                sa = SubjectAssignment(subject, lecture_hours, practical_hours)
                group.subjects[subject.name] = sa
                self.group_subject_assignments[group.name][subject.name] = sa
        self.save_group_subjects_to_csv()

    def generate_lecturers(self):
        subject_names = [subject.name for subject in self.subjects]
        for i in range(1, NUM_LECTURERS + 1):
            lecturer_name = f"Lecturer_{i}"
            num_subjects = random.randint(*LECTURER_SUBJECTS_RANGE)
            can_teach_subjects = random.sample(subject_names, k=num_subjects)
            can_conduct = ['Lecture', 'Practical']
            lecturer = Lecturer(lecturer_name, can_teach_subjects, can_conduct)
            self.lecturers.append(lecturer)
        self.save_lecturers_to_csv()

    def generate_rooms(self):
        for i in range(1, NUM_ROOMS + 1):
            room_name = f"Room_{i}"
            capacity = random.randint(*ROOM_CAPACITY_RANGE)
            room = Room(room_name, capacity)
            self.rooms.append(room)
        self.save_rooms_to_csv()

    # Save and Load Methods
    def save_groups_to_csv(self):
        with open('groups.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['GroupName', 'NumStudents', 'Subgroups'])
            for group in self.groups:
                writer.writerow([group.name, group.num_students, ",".join(group.subgroups)])

    def save_subjects_to_csv(self):
        with open('subjects.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['SubjectName', 'RequiresSubgroups'])
            for subject in self.subjects:
                writer.writerow([subject.name, 'Yes' if subject.requires_subgroups else 'No'])

    def save_group_subjects_to_csv(self):
        with open('group_subjects.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['GroupName', 'SubjectName', 'LectureHours', 'PracticalHours'])
            for group in self.groups:
                for subject_name, sa in group.subjects.items():
                    writer.writerow([group.name, subject_name, sa.lecture_hours, sa.practical_hours])

    def save_lecturers_to_csv(self):
        with open('lecturers.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['LecturerName', 'CanTeachSubjects', 'CanConduct'])
            for lecturer in self.lecturers:
                writer.writerow([lecturer.name, ",".join(lecturer.can_teach_subjects), ",".join(lecturer.can_conduct)])

    def save_rooms_to_csv(self):
        with open('rooms.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['RoomName', 'Capacity'])
            for room in self.rooms:
                writer.writerow([room.name, room.capacity])

    def read_csv_to_dict(self, filename):
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)

    def load_data(self):
        self.groups = []
        self.subjects = []
        self.lecturers = []
        self.rooms = []
        self.group_subject_assignments = defaultdict(dict)

        group_dicts = self.read_csv_to_dict('groups.csv')
        for gd in group_dicts:
            group = Group(gd['GroupName'], int(gd['NumStudents']))
            group.subgroups = gd['Subgroups'].split(',')
            self.groups.append(group)

        subject_dicts = self.read_csv_to_dict('subjects.csv')
        for sd in subject_dicts:
            subject = Subject(
                sd['SubjectName'],
                sd['RequiresSubgroups'] == 'Yes'
            )
            self.subjects.append(subject)

        group_subjects_dicts = self.read_csv_to_dict('group_subjects.csv')
        for gsd in group_subjects_dicts:
            group_name = gsd['GroupName']
            subject_name = gsd['SubjectName']
            lecture_hours = int(gsd['LectureHours'])
            practical_hours = int(gsd['PracticalHours'])
            group = next((g for g in self.groups if g.name == group_name), None)
            subject = next((s for s in self.subjects if s.name == subject_name), None)
            if group and subject:
                sa = SubjectAssignment(subject, lecture_hours, practical_hours)
                group.subjects[subject.name] = sa
                self.group_subject_assignments[group.name][subject.name] = sa

        lecturer_dicts = self.read_csv_to_dict('lecturers.csv')
        for ld in lecturer_dicts:
            lecturer = Lecturer(
                ld['LecturerName'],
                ld['CanTeachSubjects'].split(','),
                ld['CanConduct'].split(',')
            )
            self.lecturers.append(lecturer)

        room_dicts = self.read_csv_to_dict('rooms.csv')
        for rd in room_dicts:
            room = Room(rd['RoomName'], int(rd['Capacity']))
            self.rooms.append(room)

    def generate_daily_periods(self):
        self.daily_periods = []
        fixed_periods = [
            {'period_index': 0, 'start_time': 8 * 60 + 40, 'end_time': 10 * 60 + 10},   # 8:40 - 10:10
            {'period_index': 1, 'start_time': 10 * 60 + 35, 'end_time': 12 * 60 + 5},   # 10:35 - 12:05
            {'period_index': 2, 'start_time': 12 * 60 + 20, 'end_time': 13 * 60 + 50}   # 12:20 - 13:50
        ]
        for day in range(DAYS_PER_WEEK):
            day_periods = []
            for period_info in fixed_periods:
                day_periods.append({
                    'day': day,
                    'period_index': period_info['period_index'],
                    'start_time': period_info['start_time'],
                    'end_time': period_info['end_time']
                })
            self.daily_periods.append(day_periods)

    def create_schedule(self):
        # Generate daily periods
        self.generate_daily_periods()

        # Generate time slots
        self.time_slots = []
        for week in range(SEMESTER_WEEKS):
            for day_index, periods in enumerate(self.daily_periods):
                for period in periods:
                    period_index = period['period_index']
                    self.time_slots.append((week, day_index, period_index))

                    # Initialize availability to True
                    for lecturer in self.lecturers:
                        self.lecturer_availability[lecturer.name][week][day_index][period_index] = True
                    for group in self.groups + [Group(sg, group.num_students // 2) for group in self.groups for sg in group.subgroups]:
                        self.group_availability[group.name][week][day_index][period_index] = True
                    for room in self.rooms:
                        self.room_availability[room.name][week][day_index][period_index] = True

        # Schedule lectures and practicals
        self.schedule_classes()

    def schedule_classes(self):
        schedule_changed = True
        while schedule_changed:
            schedule_changed = False
            for class_type in ['Lecture', 'Practical']:
                for group in self.groups:
                    for subject_name, sa in group.subjects.items():
                        subject = sa.subject
                        if class_type == 'Lecture':
                            hours_needed = sa.lecture_hours - sa.lecture_hours_scheduled
                        else:
                            hours_needed = sa.practical_hours - sa.practical_hours_scheduled
                        if hours_needed <= 0:
                            continue
                        if class_type == 'Practical' and subject.requires_subgroups:
                            practical_hours_per_subgroup = sa.practical_hours / len(group.subgroups)
                            for subgroup_name in group.subgroups:
                                subgroup = Group(subgroup_name, group.num_students // 2)
                                sub_sa = self.group_subject_assignments[subgroup_name].get(subject_name)
                                if not sub_sa:
                                    sub_sa = SubjectAssignment(subject, 0, practical_hours_per_subgroup)
                                    self.group_subject_assignments[subgroup_name][subject_name] = sub_sa
                                sub_hours_needed = sub_sa.practical_hours - sub_sa.practical_hours_scheduled
                                while sub_hours_needed > 0:
                                    success = self.schedule_class(subgroup, subject, class_type, main_group=group)
                                    if success:
                                        schedule_changed = True
                                        sub_hours_needed -= 1.5
                                    else:
                                        break
                        else:
                            while hours_needed > 0:
                                success = self.schedule_class(group, subject, class_type)
                                if success:
                                    schedule_changed = True
                                    hours_needed -= 1.5
                                else:
                                    break

    def schedule_class(self, group, subject, class_type, main_group=None):
        random.shuffle(self.time_slots)  # Shuffle to distribute classes more evenly
        for week, day, period_index in self.time_slots:
            period_info = next((p for p in self.daily_periods[day] if p['period_index'] == period_index), None)
            if not period_info:
                continue
            # Check group availability
            if not self.group_availability[group.name][week][day][period_index]:
                continue
            if main_group and not self.group_availability[main_group.name][week][day][period_index]:
                continue  # Ensure main group is available when scheduling subgroups

            # Find eligible lecturers
            eligible_lecturers = [lecturer for lecturer in self.lecturers
                                  if subject.name in lecturer.can_teach_subjects and class_type in lecturer.can_conduct
                                  and self.lecturer_availability[lecturer.name][week][day][period_index]]

            if not eligible_lecturers:
                continue

            lecturer = random.choice(eligible_lecturers)

            sa = self.group_subject_assignments[group.name][subject.name]

            # Check if scheduling this class would exceed required hours
            if class_type == 'Lecture':
                # For combined groups, check all groups
                if main_group is None:
                    # This is a lecture for the main group (could be combined with other groups)
                    combined_groups = [group]
                    for other_group in self.groups:
                        if other_group.name == group.name:
                            continue
                        sa_other = other_group.subjects.get(subject.name)
                        if sa_other and sa_other.lecture_hours_scheduled + 1.5 <= sa_other.lecture_hours:
                            if self.group_availability[other_group.name][week][day][period_index]:
                                combined_groups.append(other_group)
                    # Before scheduling, ensure none of the combined groups would exceed their required hours
                    over_schedule = False
                    for g in combined_groups:
                        sa_g = self.group_subject_assignments[g.name][subject.name]
                        if sa_g.lecture_hours_scheduled + 1.5 > sa_g.lecture_hours:
                            over_schedule = True
                            break
                    if over_schedule:
                        continue  # Cannot schedule as it would over-schedule one of the groups
                    # Find suitable room
                    total_students = sum(g.num_students for g in combined_groups)
                    suitable_rooms = [room for room in self.rooms if
                                      self.room_availability[room.name][week][day][period_index] and room.capacity >= total_students]
                    if not suitable_rooms:
                        continue
                    room = suitable_rooms[self.room_assignment_index % len(suitable_rooms)]
                    self.room_assignment_index += 1
                    # Schedule the class
                    class_info = {
                        'Groups': [g.name for g in combined_groups],
                        'Subject': subject.name,
                        'Lecturer': lecturer.name,
                        'Room': room.name,
                        'Type': class_type,
                        'Day': day,
                        'PeriodIndex': period_index,
                        'Week': week,
                        'TotalStudents': total_students,
                        'RoomCapacity': room.capacity
                    }
                    self.schedule[(week, day, period_index)].append(class_info)
                    # Update availability
                    self.lecturer_availability[lecturer.name][week][day][period_index] = False
                    self.room_availability[room.name][week][day][period_index] = False
                    for g in combined_groups:
                        self.group_availability[g.name][week][day][period_index] = False
                        sa_g = self.group_subject_assignments[g.name][subject.name]
                        sa_g.lecture_hours_scheduled += 1.5
                    return True
                else:
                    # Should not reach here
                    continue
            else:
                # For practicals, check if scheduling would exceed required hours
                if sa.practical_hours_scheduled + 1.5 > sa.practical_hours:
                    continue  # Skip to prevent over-scheduling
                # For subgroups, also check main group's practical hours
                if main_group:
                    main_sa = self.group_subject_assignments[main_group.name][subject.name]
                    if main_sa.practical_hours_scheduled + 1.5 > main_sa.practical_hours:
                        continue  # Skip to prevent over-scheduling
                # Find suitable room
                num_students = group.num_students
                suitable_rooms = [room for room in self.rooms if
                                  self.room_availability[room.name][week][day][period_index] and room.capacity >= num_students]
                if not suitable_rooms:
                    continue
                room = suitable_rooms[self.room_assignment_index % len(suitable_rooms)]
                self.room_assignment_index += 1
                # Schedule the class
                class_info = {
                    'Groups': [group.name],
                    'Subject': subject.name,
                    'Lecturer': lecturer.name,
                    'Room': room.name,
                    'Type': class_type,
                    'Day': day,
                    'PeriodIndex': period_index,
                    'Week': week,
                    'TotalStudents': num_students,
                    'RoomCapacity': room.capacity
                }
                self.schedule[(week, day, period_index)].append(class_info)
                # Update availability
                self.lecturer_availability[lecturer.name][week][day][period_index] = False
                self.room_availability[room.name][week][day][period_index] = False
                self.group_availability[group.name][week][day][period_index] = False
                if main_group:
                    self.group_availability[main_group.name][week][day][period_index] = False
                # Update scheduled practical hours
                sa.practical_hours_scheduled += 1.5
                if main_group:
                    main_sa = self.group_subject_assignments[main_group.name][subject.name]
                    main_sa.practical_hours_scheduled += 1.5
                return True
        return False

    def print_schedule(self):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
        for week in range(SEMESTER_WEEKS):
            print(f"\nWeek {week+1}:")
            for day_index in range(DAYS_PER_WEEK):
                print(f"  {days[day_index]}:")
                periods = self.daily_periods[day_index]
                for period in periods:
                    period_index = period['period_index']
                    start_time = period['start_time']
                    end_time = period['end_time']
                    start_time_str = f"{start_time // 60}:{start_time % 60:02d}"
                    end_time_str = f"{end_time // 60}:{end_time % 60:02d}"
                    classes = self.schedule.get((week, day_index, period_index), [])
                    if classes:
                        print(f"    Period {period_index + 1} ({start_time_str}-{end_time_str}):")
                        for class_info in classes:
                            groups_str = ', '.join(class_info['Groups'])
                            lecturer_name = class_info['Lecturer']
                            total_students = class_info['TotalStudents']
                            room_capacity = class_info['RoomCapacity']
                            print(f"      {class_info['Type']} - {class_info['Subject']} - Groups: {groups_str}")
                            print(f"        Lecturer: {lecturer_name}")
                            print(f"        Room: {class_info['Room']} (Capacity: {room_capacity}) - Total Students: {total_students}")

    def print_group_programs(self):
        print("\nGroup Programs and Fulfillment:")
        for group in self.groups:
            print(f"\nProgram for {group.name}:")
            for subject_name, sa in group.subjects.items():
                lecture_diff = sa.lecture_hours_scheduled - sa.lecture_hours
                practical_diff = sa.practical_hours_scheduled - sa.practical_hours
                lecture_status = f"{sa.lecture_hours_scheduled}/{sa.lecture_hours}"
                practical_status = f"{sa.practical_hours_scheduled}/{sa.practical_hours}"
                print(f"  Subject: {subject_name}")
                print(f"    Lectures: {lecture_status} hours (Difference: {lecture_diff})")
                print(f"    Practicals: {practical_status} hours (Difference: {practical_diff})")

    def calculate_penalties(self):
        total_penalty = 0
        for group in self.groups:
            for subject_name, sa in group.subjects.items():
                lecture_diff = sa.lecture_hours_scheduled - sa.lecture_hours
                practical_diff = sa.practical_hours_scheduled - sa.practical_hours
                penalty = abs(lecture_diff) + abs(practical_diff)
                total_penalty += penalty
        print(f"\nTotal scheduling penalty (sum of differences in hours): {total_penalty}")

    def print_lecturer_assignments(self):
        print("\nLecturer Assignments:")
        for lecturer in self.lecturers:
            subjects = ', '.join(lecturer.can_teach_subjects)
            conducts = ', '.join(lecturer.can_conduct)
            print(f"{lecturer.name}:")
            print(f"  Subjects: {subjects}")
            print(f"  Can Conduct: {conducts}")

    def main(self):
        # Generate data
        self.generate_groups()
        self.generate_subjects()
        self.assign_subjects_to_groups()
        self.generate_lecturers()
        self.generate_rooms()

        # Load data
        self.load_data()

        # Create schedule
        self.create_schedule()

        # Print schedule
        self.print_schedule()

        # Print group programs and fulfillment
        self.print_group_programs()

        # Calculate penalties
        self.calculate_penalties()

        # Print lecturer assignments
        self.print_lecturer_assignments()

if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.main()
