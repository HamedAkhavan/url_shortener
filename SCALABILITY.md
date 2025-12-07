# Questions

- heavy logging:
    1. We can offload the logging from request handling path and make it async by putting a small message in a queue and logging messages in the queue from a separate service.
    2. We can use a sidecar to collect logs from main service.
    3. We can store logs in a temporary storage and store them on main storage in batch.

- multi-instance:
    - shared database must be used for all instances.
    - caching must be external and be shared between instances.
    - logging must become centralized (not local log for each instance).
    - risks:
        - race condition: multiple instances try to modify same resource.
        - load balancing: instances must have health checks and loads must be routed to healthy instances.

- heavy load:
    1. horizontal scaling dynamically: for example from 2 instance to 4 instances.
    2. using CDNs and using caching.
    3. caching on server: for example using redis to cache short_codes and its original urls.
    4. applying rate limiting (or more strict rate limiting) strategy.
    5. creating more read replicas for db.