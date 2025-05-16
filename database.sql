
CREATE TABLE urls (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);


CREATE TABLE url_checks (
  id SERIAL PRIMARY KEY,
  url_id INT REFERENCES urls (id),
  status_code INT,
  h1 VARCHAR(100),
  title VARCHAR(100),
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

