# SEMS Transaction, Concurrency and Recovery Report

**Course mapping:** ETCS302 Unit IV  
**Production engine:** MySQL 8.4.11 / InnoDB  
**Safety:** destructive/concurrent teaching exercises use `sems_academic_demo` or a dedicated `sems_test`, never valued `sems_db` data.

## Transaction model in the application

`db/session.py` defines the Python transaction boundary. A service opens a session, revalidates the actor, reads/locks required rows, validates the full state transition, performs all writes, and commits only when the context exits successfully. Any exception rolls back the complete unit of work and closes the session.

| Business transaction | Atomic facts | Locking/consistency requirement |
|---|---|---|
| Request review | every request line and derived header state | header/lines locked; every line requires an outcome |
| Transfer approval | approval state plus available→reserved changes | source inventory locked in ascending ID order; all allocations succeed or none |
| Cancel approved transfer | status plus reserved→available release | same exact source positions locked |
| Dispatch | dispatch metadata plus reserved decrement | reserved stock cannot be decremented twice |
| Receipt | received quantities, receiver/date and destination stock increments | source transfer rows and selected/created destination positions validated/locked |
| Temporary return | line return data plus source/destination stock movement | complete selected lines; all relevant rows locked consistently |
| Disposal | disposal history row plus free-stock decrement | one inventory row locked; reserved stock is not disposed |

## ACID with SEMS examples

- **Atomicity:** a five-line transfer approval reserves all five allocations or rolls back every reservation.
- **Consistency:** quantities remain non-negative, requested/approved/sent/received ceilings hold, FKs remain valid and workflow states advance only through allowed transitions.
- **Isolation:** row locks prevent another session from allocating the same free quantity before the first transaction completes.
- **Durability:** after COMMIT, InnoDB recovery mechanisms preserve the accepted change across process/server restart, subject to configured durability settings.

## Transaction states

An SEMS service transaction is **active** while validating/locking/updating. After its final statement it is **partially committed** until MySQL makes COMMIT durable. It then becomes **committed**. An error produces **failed**, rollback makes it **aborted**, and the caller may correct input or retry a deadlock victim as a new transaction. Application lifecycle states such as APPROVED or DISPATCHED are domain states, not DBMS transaction states.

## Schedules and serializability

A **serial schedule** completes one transfer allocation before another begins. A **concurrent schedule** interleaves their operations for throughput. A schedule is **conflict serializable** if conflicting read/write operations can be ordered equivalently to some serial execution; exclusive row locks provide the practical SEMS mechanism. **View serializability** is broader and is explained theoretically; SEMS does not implement a custom schedule analyzer.

A schedule is **recoverable** when a transaction commits only after transactions whose values it read have committed. InnoDB isolation and lock/commit behavior, combined with no dirty-write workflow, support this. Cascadeless/strict behavior is preferred because write locks are retained until commit.

## Lost-update/over-allocation scenario

Suppose inventory position 1 has 10 free units and two Lab Assistants each attempt to reserve 7.

1. Session A starts a transaction and selects position 1 `FOR UPDATE`.
2. Session A verifies 10 ≥ 7 and changes free/reserved to 3/7.
3. Session B requests the same row lock and waits.
4. A commits; B obtains the lock and re-reads free quantity 3.
5. B's guarded update/validation rejects 7, so total reservation never reaches 14.

Run the isolated two-tab script in `academic_demo/sql/10_concurrency_demo.sql`. It is manual because one sequential script cannot demonstrate a real lock wait.

## Locking model

- a shared lock concept allows compatible readers; an exclusive lock protects a write target;
- InnoDB provides record/next-key locking according to statement and isolation level;
- SEMS mutable stock reads use SQLAlchemy `.with_for_update()`, producing `SELECT ... FOR UPDATE`;
- multi-position operations sort unique `inventory_id` values first, producing a stable lock order;
- transactions remain short and do not wait for user input while holding locks;
- appropriate indexes reduce scanned/locked rows.

The configured application isolation level is READ COMMITTED. It prevents dirty reads while reducing long-lived snapshot/gap effects for this interactive workload. Correctness does not depend on a user reading an unlocked value and later overwriting it: stock transitions re-read/lock the target rows.

## Isolation phenomena

| Phenomenon | Meaning | SEMS treatment |
|---|---|---|
| Dirty read | read uncommitted data that may roll back | prevented by READ COMMITTED |
| Lost update | later write overwrites an intervening write | prevented for stock via row locks and guarded arithmetic |
| Non-repeatable read | same row returns a newly committed value later | possible for ordinary unlocked reads at READ COMMITTED; workflow rows are locked where stability matters |
| Phantom | repeated predicate returns newly committed rows | possible at READ COMMITTED; exact PK rows are locked for stock transitions and ceilings are revalidated |

Timestamp ordering is covered theoretically as an alternative concurrency-control family; SEMS correctly uses InnoDB locking rather than implementing a second transaction scheduler.

## Deadlock

A deadlock can occur when Session A holds row 1 and waits for row 2 while Session B holds row 2 and waits for row 1. InnoDB detects the cycle, chooses a victim and normally reports error 1213 / SQLSTATE 40001. The victim transaction must be fully rolled back and, where appropriate, retried from the start—not resumed halfway.

SEMS reduces risk by sorting inventory locks, keeping transactions short and using indexed predicates. `academic_demo/sql/11_deadlock_demo.sql` creates two disposable rows and provides a two-session faculty exercise. Never run it against production inventory.

## TCL and savepoints

`academic_demo/sql/09_transactions_savepoints.sql` demonstrates `START TRANSACTION`, `SAVEPOINT`, `ROLLBACK TO SAVEPOINT`, `RELEASE SAVEPOINT`, `COMMIT` and full `ROLLBACK`. The production Python services normally use all-or-nothing transactions; a savepoint is demonstrated academically because partial recovery is legitimate in a controlled batch, not because every workflow should partially commit.

## Recovery and checkpoints

- **undo** information supports rollback and consistent reads;
- **redo** information supports reapplying committed changes during crash recovery;
- **write-ahead logging** means required log information reaches durable storage before the corresponding data page is considered durable;
- **checkpoints** bound recovery work by establishing a progress point between log and data-page state;
- after a crash, InnoDB performs recovery using its logs: committed work is redone as required and incomplete work is undone;
- normal faculty evidence should demonstrate ROLLBACK, not crash a server or manipulate logs.

Backup/restore, server-level durability configuration and disaster recovery are operational administration topics outside the application MVP. They must be configured and tested for any real departmental deployment.

## Production versus academic-only evidence

| Concept | Production implementation | Academic demonstration/documentation |
|---|---|---|
| atomic stock workflows | yes, Python service transactions | tests and viva trace |
| row locking | yes, ordered `FOR UPDATE` | two-session allocation demo |
| rollback on exception | yes | savepoint/full rollback demo |
| deadlock prevention | stable lock order | intentionally induced only in demo schema |
| deadlock retry | safe rollback behavior; no broad automatic retry loop claimed | error/victim explanation |
| crash recovery/checkpoint | provided by configured InnoDB server | theory only; no destructive simulation |
| timestamp ordering | no | theoretical comparison |
| schedule analyzer | no | serializability concepts documented |

## Faculty sequence

1. show `get_inventory_rows_for_update()` and one transfer service transaction;
2. run the savepoint demo in one Workbench tab;
3. run concurrency Session A/B blocks in two tabs and explain the wait/recheck;
4. optionally use the isolated deadlock rows, observe one victim, then issue ROLLBACK in both tabs;
5. state which mechanisms are production and which are teaching-only.

## Viva answer

> SEMS treats transfer approval as one transaction. It locks every source INVENTORY row in ascending ID order, verifies all quantities, and moves each approved quantity from available to reserved. If any line fails, the context rolls back the whole approval. Stable lock order reduces deadlocks; InnoDB still detects a cycle and the victim must retry the complete transaction.

