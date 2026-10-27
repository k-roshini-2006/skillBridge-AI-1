"""
Run with: python seed_data.py
Populates courses, topics, extensive question bank, grounded study materials for RAG,
demo accounts for Student, Teacher, and Admin, notifications, and badges.
"""
from datetime import datetime
from app.db.base import Base, SessionLocal, engine
from app.models.models import (
    Course, DifficultyEnum, Question, Topic, StudyMaterial,
    User, Student, Teacher, Admin, Streak, RoleEnum,
    CompetencyScore, CompetencyLevelEnum, Badge, Notification
)
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

COURSES = {
    "Data Structures": ["Arrays", "Linked List", "Stack", "Queue", "Trees", "Graphs"],
}

SAMPLE_QUESTIONS = {
    "Arrays": [
        ("What is the time complexity of accessing an element by index in an array?",
         {"a": "O(1)", "b": "O(n)", "c": "O(log n)", "d": "O(n^2)"}, "a",
         "Array access uses direct memory addressing (base_address + index * element_size), giving O(1) constant time.",
         "Understand array contiguous memory layout", "Remember"),
        ("Which operation is most expensive in a standard dynamic array?",
         {"a": "Read element by index", "b": "Insert at end (amortized)", "c": "Insert at beginning", "d": "In-place update"}, "c",
         "Inserting at index 0 requires shifting all N existing elements rightward by 1 position, resulting in O(N) time.",
         "Analyze array insertion costs", "Analyze"),
        ("What is the amortized time complexity of appending an element to a dynamic array (like Python list or Java ArrayList)?",
         {"a": "O(1)", "b": "O(n)", "c": "O(log n)", "d": "O(n^2)"}, "a",
         "Although resizing copies N elements, doubling capacity means resizes happen exponentially less frequently, averaging O(1) per append.",
         "Evaluate amortized geometric doubling", "Understand"),
        ("Which two-pointer approach finds a pair summing to a target in a strictly sorted array in O(n) time?",
         {"a": "Both pointers start at index 0", "b": "One pointer at index 0, one at index N-1, moving inward based on sum", "c": "Fast and slow pointers moving at 2x and 1x speed", "d": "Random binary jumps"}, "b",
         "Since the array is sorted, if pair sum < target, advance left pointer; if pair sum > target, decrement right pointer.",
         "Apply two-pointer convergence pattern", "Apply"),
        ("In multidimensional arrays stored in row-major order, how are elements arranged in physical RAM?",
         {"a": "Column by column", "b": "Consecutive rows laid out sequentially in contiguous memory", "c": "Linked via pointer references", "d": "Hashed into buckets"}, "b",
         "Row-major order stores row 0 elements, followed immediately by row 1 elements, maximizing CPU cache locality.",
         "Analyze cache performance and memory layout", "Understand"),
    ],
    "Linked List": [
        ("What is the time complexity of inserting a new node at the head of a singly linked list?",
         {"a": "O(1)", "b": "O(n)", "c": "O(log n)", "d": "O(n log n)"}, "a",
         "Head insertion only requires creating the new node, pointing its next to the current head, and reassigning the head pointer.",
         "Understand linked list pointer operations", "Remember"),
        ("To delete a node given ONLY a pointer to that node (not head) in a singly linked list, what is the standard trick?",
         {"a": "Copy the next node's data into current node, then bypass and delete the next node", "b": "It is mathematically impossible", "c": "Traverse backward using null pointer", "d": "Allocate a temporary stack"}, "a",
         "Since backward traversal is impossible without the previous pointer, copying the successor's data forward converts it into deleting the successor node.",
         "Apply pointer manipulation for in-place deletion", "Apply"),
        ("Which algorithm detects cycles in a linked list using O(1) auxiliary space?",
         {"a": "Dijkstra's Algorithm", "b": "Floyd's Tortoise and Hare (Fast & Slow Pointers)", "c": "Binary Search", "d": "Topological Sort"}, "b",
         "Floyd's algorithm uses a slow pointer moving 1 step and a fast pointer moving 2 steps; if a cycle exists, they must collide.",
         "Analyze cycle detection mechanics", "Understand"),
        ("What is the time complexity to find the K-th element from the end of a singly linked list in a single pass?",
         {"a": "O(N) using two pointers spaced K steps apart", "b": "O(N^2)", "c": "O(log N)", "d": "O(1)"}, "a",
         "Advance the first pointer K steps ahead; then advance both pointers simultaneously until the first reaches the end.",
         "Apply two-pointer window spacing", "Apply"),
        ("What is the primary memory overhead drawback of a doubly linked list over a singly linked list?",
         {"a": "Doubly linked lists cannot store objects", "b": "Each node requires an additional previous pointer, consuming more RAM per node", "c": "Traversing forward is O(N^2)", "d": "Garbage collectors cannot free doubly linked lists"}, "b",
         "Every node holds both a 'next' pointer and a 'prev' pointer, which doubles the pointer storage overhead.",
         "Evaluate memory tradeoffs of node structures", "Analyze"),
    ],
    "Stack": [
        ("Which fundamental principle defines stack behavior?",
         {"a": "FIFO (First-In, First-Out)", "b": "LIFO (Last-In, First-Out)", "c": "Priority-based Preemption", "d": "Direct Random Access"}, "b",
         "Stacks enforce Last-In, First-Out: the most recently pushed element is the first one popped.",
         "Understand stack semantics", "Remember"),
        ("Which data structure is naturally used by compilers and CPU runtimes to manage nested function calls and local variables?",
         {"a": "Call Stack", "b": "Circular Queue", "c": "B-Tree", "d": "Disjoint Set"}, "a",
         "The call stack preserves return addresses and stack frames for nested or recursive function calls.",
         "Understand recursion call stack mechanics", "Understand"),
        ("What is the time complexity to find the Next Greater Element for every element in an array of size N using a Monotonic Stack?",
         {"a": "O(N) because each element is pushed and popped at most once", "b": "O(N^2)", "c": "O(N log N)", "d": "O(log N)"}, "a",
         "Even though there is a nested while loop inside the iteration, each element is pushed and popped exactly once, yielding amortized O(N) total time.",
         "Apply monotonic stack pattern", "Apply"),
        ("When converting an Infix arithmetic expression (e.g. A + B * C) to Postfix (A B C * +), what role does the stack play?",
         {"a": "Stores operands in reverse", "b": "Holds operators and enforces operator precedence and parentheses", "c": "Evaluates numerical calculations immediately", "d": "Acts as a hash table"}, "b",
         "Operators are pushed to the stack and popped to the output based on precedence hierarchy and parentheses bounds.",
         "Analyze infix to postfix conversion algorithm", "Analyze"),
    ],
    "Queue": [
        ("Which principle does a standard linear queue follow?",
         {"a": "FIFO (First-In, First-Out)", "b": "LIFO (Last-In, First-Out)", "c": "Round Robin Only", "d": "Random Access"}, "a",
         "Queues strictly preserve arrival order: the first element enqueued is the first dequeued.",
         "Understand queue semantics", "Remember"),
        ("How does a Circular Queue solve the memory-wasting problem of a fixed linear array queue?",
         {"a": "It uses modulo arithmetic `(index + 1) % capacity` to wrap around to freed front positions", "b": "It doubles array size on every dequeue", "c": "It shifts all elements left on every dequeue", "d": "It converts elements to pointers"}, "a",
         "Modulo arithmetic enables the rear pointer to wrap around to index 0 when front items have been dequeued, reusing freed slots in O(1) time.",
         "Apply circular buffer pointer arithmetic", "Apply"),
        ("In an Operating System CPU scheduler, which queue variation allows processes with higher priority to execute first?",
         {"a": "Priority Queue (often backed by a Heap)", "b": "Monotonic Stack", "c": "Singly Linked List", "d": "Simple FIFO Queue"}, "a",
         "Priority queues dequeue items based on highest priority (or lowest deadline) rather than strict arrival sequence.",
         "Understand scheduling priority structures", "Understand"),
        ("What is the time complexity of enqueuing and dequeuing in an array-based circular queue?",
         {"a": "O(1) for both enqueue and dequeue", "b": "O(N) for enqueue, O(1) for dequeue", "c": "O(log N)", "d": "O(N)"}, "a",
         "Circular queues update front and rear indices using modular increment, executing both operations in O(1) constant time without shifting.",
         "Analyze circular queue runtime complexity", "Analyze"),
    ],
    "Trees": [
        ("In a Binary Search Tree (BST), what is the key invariant regarding child nodes?",
         {"a": "Left child value < Root value < Right child value", "b": "Left child value > Root value", "c": "All leaves must be on the same level", "d": "Every node must have two children"}, "a",
         "The BST invariant dictates that for any node X, all values in its left subtree are strictly smaller than X, and all values in its right subtree are strictly greater.",
         "Understand BST ordering invariant", "Remember"),
        ("Which tree traversal of a BST outputs the stored elements in strictly ascending sorted order?",
         {"a": "Pre-order (Root, Left, Right)", "b": "In-order (Left, Root, Right)", "c": "Post-order (Left, Right, Root)", "d": "Level-order (Breadth-First)"}, "b",
         "In-order traversal visits all smaller elements in the left subtree first, then visits the node, then visits all larger elements in the right subtree.",
         "Understand BST traversal properties", "Understand"),
        ("In a balanced Binary Search Tree (like an AVL or Red-Black Tree) with N nodes, what is the height H?",
         {"a": "H = O(log N)", "b": "H = O(N)", "c": "H = O(1)", "d": "H = O(N^2)"}, "a",
         "Self-balancing rotations ensure the tree height remains bounded by O(log N), guaranteeing O(log N) searches, insertions, and deletions.",
         "Analyze balanced tree height bounds", "Analyze"),
        ("In an AVL tree, what is the maximum permissible difference in height between the left and right subtrees of any node?",
         {"a": "0", "b": "1", "c": "2", "d": "No limit"}, "b",
         "The AVL balance factor must be in {-1, 0, 1}. A difference of 2 triggers single or double rotation to restore balance.",
         "Evaluate AVL tree rotation triggers", "Apply"),
    ],
    "Graphs": [
        ("Which traversal algorithm uses a FIFO Queue and explores vertices level by level from the source?",
         {"a": "Breadth-First Search (BFS)", "b": "Depth-First Search (DFS)", "c": "Bellman-Ford", "d": "Kruskal's Algorithm"}, "a",
         "BFS systematically discovers all vertices at distance k before moving to distance k+1 using a queue.",
         "Differentiate BFS and DFS mechanics", "Remember"),
        ("What is the time complexity of Breadth-First Search (BFS) and Depth-First Search (DFS) on a graph with V vertices and E edges represented as an adjacency list?",
         {"a": "O(V + E)", "b": "O(V * E)", "c": "O(V^2)", "d": "O(E log V)"}, "a",
         "Each vertex is enqueued/visited once, and each edge is traversed once (directed) or twice (undirected), leading to O(V + E) time.",
         "Analyze graph traversal complexity", "Analyze"),
        ("Which algorithm is used to find the shortest path in a graph with non-negative edge weights?",
         {"a": "Dijkstra's Algorithm", "b": "Prim's Algorithm", "c": "Tarjan's Algorithm", "d": "Kosaraju's Algorithm"}, "a",
         "Dijkstra's greedy algorithm finds the shortest path from a source to all other vertices in non-negative weighted graphs using a priority queue.",
         "Apply shortest path algorithms", "Apply"),
        ("Which algorithm detects cycles in an undirected graph by checking if two vertices share the same representative set?",
         {"a": "Union-Find (Disjoint Set Union)", "b": "Floyd-Warshall", "c": "Ford-Fulkerson", "d": "Edmonds-Karp"}, "a",
         "If the endpoints u and v of an edge (u, v) already have the same set representative, adding the edge creates a cycle.",
         "Apply Disjoint Set Union to cycle detection", "Apply"),
        ("What is the purpose of Topological Sort in a Directed Acyclic Graph (DAG)?",
         {"a": "To linearize vertices such that for every directed edge u -> v, u appears before v", "b": "To find the shortest path in negative weight cycles", "c": "To convert a graph into a binary search tree", "d": "To color the graph with 2 colors"}, "a",
         "Topological sorting represents valid dependency ordering (e.g. course prerequisites, build task execution).",
         "Understand topological order semantics", "Understand"),
    ]
}

SAMPLE_MATERIALS = {
    "Arrays": [
        {
            "type": "notes",
            "title": "Comprehensive Array Mechanics & Memory Architecture",
            "source": "SkillPath Core DS Textbook",
            "content": """# Arrays: Memory Architecture & Algorithmic Operations

An array is a linear collection of elements stored in contiguous physical memory addresses.

### 1. Memory Addressing Invariant
Because elements are strictly contiguous, the memory address of element at index `i` is computed instantaneously:
`Address(A[i]) = Base_Address + (i * Element_Size_in_Bytes)`
This direct offset math guarantees O(1) random access by index.

### 2. Time & Space Complexity Breakdown
- **Access by Index:** O(1)
- **Search (Unsorted):** O(n) linear scan
- **Search (Sorted):** O(log n) via Binary Search
- **Insertion at Beginning:** O(n) — requires shifting all n elements rightward
- **Insertion at End (Dynamic Array):** Amortized O(1), worst-case O(n) during capacity resize
- **Deletion at Index k:** O(n - k) due to leftward shifting

### 3. Dynamic Array Resizing Invariant
Dynamic arrays (Python list, C++ std::vector) start with small capacity. When full:
1. Allocates a new contiguous array of size 2 * current_capacity (geometric doubling).
2. Copies all existing elements over to the new buffer.
3. Deallocates the old memory block.
Because doubling occurs at powers of 2, the total work for N appends is O(N), averaging amortized O(1) per append."""
        },
        {
            "type": "cheatsheet",
            "title": "Array Patterns & Common Algorithmic Cheatsheet",
            "source": "SkillPath Algorithmic Guide",
            "content": """# Array Cheatsheet

### Key Algorithmic Patterns:
1. **Two Pointers (Inward):**
   - For sorted arrays (e.g., Two Sum II). Left at 0, Right at N-1.
   - If sum < target: left++ | If sum > target: right--
2. **Fast & Slow Pointers (Sliding Window):**
   - For subarray sum, longest substring without repeats.
3. **Prefix Sum Array:**
   - Precompute running sum: `P[i] = P[i-1] + A[i]`.
   - Query range sum [L, R] in O(1): `Sum(L, R) = P[R] - P[L-1]`
4. **Kadane's Algorithm for Maximum Subarray:**
   - `max_ending_here = max(A[i], max_ending_here + A[i])`
   - Runs in O(n) time and O(1) auxiliary space."""
        },
        {
            "type": "interview_qs",
            "title": "Top Array Interview Challenges & Invariants",
            "source": "Tech Interview Guide 2026",
            "content": """# Array Top Interview Questions

1. **Two Sum:**
   - Brute force: O(n^2).
   - Optimal: Use Hash Map for O(n) time, O(n) space.
2. **Move Zeroes to End in Place:**
   - Two pointer technique: slow pointer tracks next non-zero write position.
3. **Product of Array Except Self:**
   - Compute prefix products from left, then suffix products from right without division operator in O(n) time and O(1) output space."""
        }
    ],
    "Linked List": [
        {
            "type": "notes",
            "title": "Linked List Foundations: Singly, Doubly & Circular",
            "source": "SkillPath Core DS Textbook",
            "content": """# Linked List Architecture & Mechanics

Unlike arrays, linked lists allocate memory dynamically for individual nodes. Nodes are non-contiguous and chained via pointers.

### Node Structure
```
Node {
    data: Value,
    next: Pointer to Node
}
```

### Time Complexity:
- **Insert at Head:** O(1)
- **Delete at Head:** O(1)
- **Insert / Delete at Tail (with tail pointer):** O(1) for insert; O(n) for singly list delete (requires finding predecessor).
- **Search / Access by index:** O(n) sequential traversal.

### Singly vs Doubly Linked Lists:
- Singly: 1 pointer per node (`next`). Lower memory overhead.
- Doubly: 2 pointers per node (`next` and `prev`). Enables O(1) deletion given pointer to node itself."""
        },
        {
            "type": "cheatsheet",
            "title": "Linked List Pointer Manipulation Cheatsheet",
            "source": "SkillPath Algorithmic Guide",
            "content": """# Linked List Pointer Cheatsheet

### 1. In-place Reversal (3 Pointers):
```python
prev = None
curr = head
while curr:
    nxt = curr.next
    curr.next = prev
    prev = curr
    curr = nxt
return prev  # New head
```

### 2. Floyd's Cycle Detection (Tortoise and Hare):
- `slow = head; fast = head`
- `while fast and fast.next: slow = slow.next; fast = fast.next.next`
- If `slow == fast`: cycle exists! Reset `slow = head`, advance both at 1 step/sec to locate cycle entry node."""
        }
    ],
    "Stack": [
        {
            "type": "notes",
            "title": "Stack Invariants, Call Stack & Monotonic Patterns",
            "source": "SkillPath Core DS Textbook",
            "content": """# Stacks: LIFO Semantics & Applications

A stack is a restricted linear container allowing insertion and removal at one end only: the Top.

### Core Operations (all O(1)):
- `push(x)`: Add item to top
- `pop()`: Remove and return top item
- `peek()`: View top item without removing
- `isEmpty()`: Return true if stack has 0 items

### Architectural Applications:
1. **CPU Call Stack:** Stores function execution frames, return pointers, and local variables.
2. **Undo / Redo buffers:** Tracks state history.
3. **Expression Parsing:** Converting infix expressions to postfix / prefix and evaluating Reverse Polish Notation (RPN).
4. **Monotonic Stacks:** Resolving nearest greater / smaller elements in arrays in linear O(N) time."""
        }
    ],
    "Queue": [
        {
            "type": "notes",
            "title": "Queues: FIFO Principle, Circular Buffers & Deques",
            "source": "SkillPath Core DS Textbook",
            "content": """# Queues: FIFO Principle & Implementation

A queue enforces First-In, First-Out (FIFO) semantics: items enter at the Rear (tail) and exit from the Front (head).

### Core Operations (all O(1)):
- `enqueue(x)`: Insert at rear
- `dequeue()`: Remove and return front element
- `peek()`: Examine front element without removal

### The Circular Queue Solution:
Linear array queues suffer from pointer drift where `front` advances rightward, stranding unused memory.
A Circular Queue wraps pointers using modular arithmetic:
- `rear = (rear + 1) % Capacity`
- `front = (front + 1) % Capacity`
- Full check: `(rear + 1) % Capacity == front` (when reserving 1 empty slot) or maintaining `count == Capacity`."""
        }
    ],
    "Trees": [
        {
            "type": "notes",
            "title": "Binary Trees, BST Invariants & Balanced Trees",
            "source": "SkillPath Core DS Textbook",
            "content": """# Binary Trees & Binary Search Trees (BST)

A tree is a hierarchical, non-linear data structure with a root node and child subtrees.

### Binary Search Tree (BST) Invariant:
For every node `P`:
- All values in `P.left` are `< P.value`
- All values in `P.right` are `> P.value`

### Standard Traversal Orders:
1. **In-Order (Left, Root, Right):** Produces strictly sorted output on BST.
2. **Pre-Order (Root, Left, Right):** Used for cloning and serializing trees.
3. **Post-Order (Left, Right, Root):** Used for bottom-up computation (e.g. subtree sizes, tree height, directory size calculations).
4. **Level-Order (BFS):** Explores row by row using a FIFO queue.

### Tree Balancing:
- Unbalanced BST search degrades to O(N) (like a linked list).
- Balanced BSTs (AVL, Red-Black) maintain height `H = O(log N)` via tree rotations, guaranteeing O(log N) operations."""
        }
    ],
    "Graphs": [
        {
            "type": "notes",
            "title": "Graph Representations, BFS/DFS Traversals & Shortest Paths",
            "source": "SkillPath Core DS Textbook",
            "content": """# Graphs: Representations & Traversal Algorithms

A graph G = (V, E) consists of a set of Vertices V and Edges E.

### Storage Representations:
1. **Adjacency Matrix:** 2D array `matrix[u][v] = 1`. Space: O(V^2). O(1) edge lookup. Best for dense graphs.
2. **Adjacency List:** Array/Map of lists. Space: O(V + E). Efficient iteration over neighbors. Best for sparse graphs.

### Core Traversal Algorithms:
1. **Breadth-First Search (BFS):**
   - Uses a FIFO Queue and visited set.
   - Finds the shortest path in unweighted graphs.
   - Time: O(V + E).
2. **Depth-First Search (DFS):**
   - Uses recursion or a LIFO Stack.
   - Used for cycle detection, topological sort, and connected components.
   - Time: O(V + E).

### Shortest Paths:
- **Unweighted:** BFS in O(V + E).
- **Non-negative Weights:** Dijkstra's Algorithm in O((V + E) log V) with Min-Heap.
- **Negative Weights:** Bellman-Ford in O(V * E). Detects negative cycles."""
        }
    ]
}

created_topics = {}

for course_name, topic_names in COURSES.items():
    course = db.query(Course).filter(Course.name == course_name).first()
    if not course:
        course = Course(name=course_name, description=f"{course_name} core curriculum")
        db.add(course)
        db.flush()

    for idx, topic_name in enumerate(topic_names):
        topic = db.query(Topic).filter(Topic.course_id == course.id, Topic.name == topic_name).first()
        if not topic:
            topic = Topic(course_id=course.id, name=topic_name, order_index=idx)
            db.add(topic)
            db.flush()

        created_topics[topic_name] = topic

        # Seed questions
        for item in SAMPLE_QUESTIONS.get(topic_name, []):
            q_text = item[0]
            options = item[1]
            correct = item[2]
            explanation = item[3]
            objective = item[4]
            bloom = item[5] if len(item) > 5 else "Understand"
            existing_q = db.query(Question).filter(Question.topic_id == topic.id, Question.question_text == q_text).first()
            if not existing_q:
                db.add(Question(
                    topic_id=topic.id,
                    difficulty=DifficultyEnum.medium,
                    bloom_level=bloom,
                    question_text=q_text,
                    options=options,
                    correct_answer=correct,
                    explanation=explanation,
                    learning_objective=objective,
                ))

        # Seed Study Materials for RAG and Study Hub
        for mat in SAMPLE_MATERIALS.get(topic_name, []):
            existing_mat = db.query(StudyMaterial).filter(StudyMaterial.topic_id == topic.id, StudyMaterial.title == mat["title"]).first()
            if not existing_mat:
                db.add(StudyMaterial(
                    topic_id=topic.id,
                    type=mat["type"],
                    title=mat["title"],
                    source=mat.get("source", "SkillPath AI Core Curriculum"),
                    content=mat["content"],
                ))

# Demo Accounts
# 1. Student
student_user = db.query(User).filter(User.email == "student@skillpath.ai").first()
if not student_user:
    student_user = User(
        email="student@skillpath.ai",
        password_hash=hash_password("password123"),
        role=RoleEnum.student,
    )
    db.add(student_user)
    db.flush()
    student = Student(
        user_id=student_user.id,
        reg_number="CS2026-0042",
        semester=4,
        department="Computer Science & Engineering",
        xp_points=1240,
    )
    db.add(student)
    db.flush()
    db.add(Streak(student_id=student.id, current_streak=5, longest_streak=12))

    # Competency scores for radar
    scores_plan = [
        ("Arrays", 0.90, CompetencyLevelEnum.strong, 0.2, "Solid understanding of contiguous memory and index addressing."),
        ("Linked List", 0.70, CompetencyLevelEnum.average, 0.8, "Good with node creation; practice two-pointer reversal."),
        ("Stack", 0.85, CompetencyLevelEnum.strong, 0.3, "Strong grasp of LIFO operations and recursion frames."),
        ("Queue", 0.60, CompetencyLevelEnum.average, 1.2, "Needs practice on circular queue wrap-around logic."),
        ("Trees", 0.40, CompetencyLevelEnum.weak, 2.5, "Struggled with tree traversals and BST invariants. Needs review."),
        ("Graphs", 0.30, CompetencyLevelEnum.weak, 3.0, "Missed BFS/DFS queue vs stack mechanics. Targeted practice recommended."),
    ]
    for topic_name, score, level, hours, reason in scores_plan:
        if topic_name in created_topics:
            db.add(CompetencyScore(
                student_id=student.id,
                topic_id=created_topics[topic_name].id,
                score_pct=score,
                level=level,
                confidence_score=0.85,
                estimated_hours=hours,
                reason_text=reason,
            ))

    # Badges
    badges_to_seed = [
        "Diagnostic Pioneer",
        "Streak Master",
        "Array Ace",
        "Adaptive Explorer"
    ]
    for b_name in badges_to_seed:
        db.add(Badge(student_id=student.id, badge_name=b_name))

    # Notifications
    sample_notifs = [
        ("streak", "🔥 5-Day Learning Streak Active! Keep up the momentum to earn Streak Master."),
        ("recommendation", "⚡ Weak topics detected in Trees and Graphs. Check your personalized daily plan."),
        ("mastery", "🏆 Array Ace badge unlocked! Scored 90% in Stage 1 & 3 assessments."),
        ("system", "👋 Welcome to SkillPath AI. Your adaptive learning path is generated and ready.")
    ]
    for n_type, msg in sample_notifs:
        db.add(Notification(user_id=student_user.id, type=n_type, message=msg, read_bool=False))

# 2. Teacher
teacher_user = db.query(User).filter(User.email == "teacher@skillpath.ai").first()
if not teacher_user:
    teacher_user = User(
        email="teacher@skillpath.ai",
        password_hash=hash_password("password123"),
        role=RoleEnum.teacher,
    )
    db.add(teacher_user)
    db.flush()
    db.add(Teacher(
        user_id=teacher_user.id,
        faculty_id="FAC-CS-101",
        assigned_courses=["Data Structures"],
        assigned_classes=["CS-4A", "CS-4B"],
    ))

# 3. Admin
admin_user = db.query(User).filter(User.email == "admin@skillpath.ai").first()
if not admin_user:
    admin_user = User(
        email="admin@skillpath.ai",
        password_hash=hash_password("password123"),
        role=RoleEnum.admin,
    )
    db.add(admin_user)
    db.flush()
    db.add(Admin(
        user_id=admin_user.id,
        admin_id="ADM-HEAD-01",
    ))

db.commit()
print("Comprehensive seed data (courses, questions, study materials, badges, notifications) inserted successfully.")
