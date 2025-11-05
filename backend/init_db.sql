CREATE TABLE papers (
    id VARCHAR PRIMARY KEY,
    title TEXT,
    year INTEGER,
    field VARCHAR,
    citation_count INTEGER
);

CREATE TABLE authors (
    id VARCHAR PRIMARY KEY,
    name VARCHAR,
    affiliation VARCHAR
);

CREATE TABLE author_paper (
    author_id VARCHAR,
    paper_id VARCHAR,
    FOREIGN KEY (author_id) REFERENCES authors(id),
    FOREIGN KEY (paper_id) REFERENCES papers(id)
);

CREATE INDEX idx_papers_year ON papers(year);
CREATE INDEX idx_papers_field ON papers(field);
CREATE INDEX idx_author_paper_author ON author_paper(author_id);
CREATE INDEX idx_author_paper_paper ON author_paper(paper_id);
