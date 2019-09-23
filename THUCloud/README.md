# 说明

数据库采用sqlite3.



## 原专家列表

table名original。

表结构如下：

```sql
CREATE TABLE original(
  id           INT        PRIMARY KEY     NOT NULL,
  name         TEXT,
  organization TEXT,
  keywords     TEXT,
  papers       TEXT,
  relations    TEXT
);
```

