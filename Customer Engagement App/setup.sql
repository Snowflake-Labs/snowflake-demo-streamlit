-- App data
--To run this app the following objects need to be created in the Snowflake account:

create or replace database customers_engagement_db;
create or replace schema customers_engagement_s;

create or replace table customers_engagement_db.customers_engagement_s.customer_engagement(
    customer text,
    project_types variant,
    number_active_project_type variant
);


-- You can populate the "customer_engagement" table choosing from either of the two following methods:
- Upload the provided "StreamingEdu_Data.csv" file located under the `assets/` folder in Snowsight (see [docs](https://docs.snowflake.com/en/user-guide/data-load-web-ui))
- Run the following insert statement:


-- Insert 50 tuples in the customer_engagement table
INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Alice Smith', ['Online Course', 'STEM Workshop', 'Robotics Club', 'Science Fair', 'Language Learning'], [78, 43, 91, 20, 65];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Bob Johnson', ['Tutoring Program', 'Virtual Field Trip', 'Mathematics Olympiad', 'Coding Bootcamp', 'Arts Festival'], [35, 82, 11, 69, 47];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Catherine Brown', ['Environmental Science Project', 'Literacy Program', 'Music Theory Course', 'History Debate Club', 'Health Education Workshop'], [58, 73, 40, 96, 17];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'David Williams', ['Coding Club', 'Language Exchange Program', 'Math Tutoring Service', 'Art Class', 'Physics Symposium'], [88, 24, 61, 15, 50];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Emily Davis', ['Robotics Workshop', 'Virtual Science Lab', 'Writing Club', 'Drama Production', 'Geography Quiz'], [22, 57, 85, 31, 78];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Frank Wilson', ['STEM Camp', 'Literature Circle', 'Chess Club', 'Poetry Slam', 'Debating Society'], [47, 90, 13, 75, 28];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Grace Taylor', ['Computer Science Competition', 'Book Club', 'Ecology Project', 'Language Workshop', 'Music Recital'], [79, 36, 68, 9, 54];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Henry Martinez', ['Math Games', 'Film Festival', 'Science Camp', 'Creative Writing Workshop', 'History Lecture Series'], [41, 84, 26, 93, 35];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Ivy Anderson', ['Online Tutoring', 'STEM Conference', 'Robotics Competition', 'Literature Festival', 'Language Exchange'], [61, 28, 75, 48, 14];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Jack Thompson', ['Mathematics Club', 'Virtual Science Fair', 'Writing Workshop', 'Theater Production', 'Geology Field Trip'], [17, 69, 92, 37, 81];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Jane Rodriguez', ['Coding Bootcamp', 'Music Ensemble', 'History Seminar', 'Art Exhibition', 'Health Fair'], [95, 42, 79, 23, 56];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'John Davis', ['STEM Workshop', 'Literacy Program', 'Chess Tournament', 'Poetry Workshop', 'Debate Club'], [33, 87, 19, 71, 44];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Karen Martinez', ['Language Learning Program', 'Science Symposium', 'Music Theory Class', 'Environmental Cleanup', 'Math Competition'], [71, 14, 57, 83, 25];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Kevin Nguyen', ['Robotics Workshop', 'Literature Circle', 'Coding Club', 'Music Recital', 'Health Education Program'], [13, 58, 86, 30, 77];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Linda Lee', ['STEM Camp', 'Book Club', 'Chess Club', 'Drama Club', 'Language Workshop'], [55, 98, 21, 64, 6];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Mark Garcia', ['Math Games Competition', 'Film Festival', 'Science Camp', 'Creative Writing Workshop', 'History Lecture Series'], [72, 27, 94, 38, 80];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Mary Taylor', ['Computer Science Competition', 'Book Club', 'Ecology Project', 'Language Workshop', 'Music Recital'], [29, 76, 10, 52, 89];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Michael Smith', ['Online Course', 'STEM Workshop', 'Robotics Club', 'Science Fair', 'Language Learning'], [46, 2, 39, 67, 97];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Nancy Johnson', ['Tutoring Program', 'Virtual Field Trip', 'Mathematics Olympiad', 'Coding Bootcamp', 'Arts Festival'], [4, 51, 99, 45, 32];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Olivia Brown', ['Environmental Science Project', 'Literacy Program', 'Music Theory Course', 'History Debate Club', 'Health Education Workshop'], [51, 8, 45, 100, 1];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Patrick Williams', ['Coding Club', 'Language Exchange Program', 'Math Tutoring Service', 'Art Class', 'Physics Symposium'], [24, 62, 6, 98, 42];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Rachel Davis', ['Robotics Workshop', 'Virtual Science Lab', 'Writing Club', 'Drama Production', 'Geography Quiz'], [92, 16, 73, 19, 87];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Robert Wilson', ['STEM Camp', 'Literature Circle', 'Chess Club', 'Poetry Slam', 'Debating Society'], [36, 71, 0, 55, 93];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Sarah Taylor', ['Computer Science Competition', 'Book Club', 'Ecology Project', 'Language Workshop', 'Music Recital'], [83, 32, 68, 14, 60];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Steven Martinez', ['Math Games', 'Film Festival', 'Science Camp', 'Creative Writing Workshop', 'History Lecture Series'], [8, 79, 26, 91, 40];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Susan Anderson', ['Online Tutoring', 'STEM Conference', 'Robotics Competition', 'Literature Festival', 'Language Exchange'], [65, 12, 63, 24, 70];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Thomas Thompson', ['Mathematics Club', 'Virtual Science Fair', 'Writing Workshop', 'Theater Production', 'Geology Field Trip'], [38, 84, 16, 72, 3];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Vanessa Rodriguez', ['Coding Bootcamp', 'Music Ensemble', 'History Seminar', 'Art Exhibition', 'Health Fair'], [80, 31, 89, 5, 49];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'William Davis', ['STEM Workshop', 'Literacy Program', 'Chess Tournament', 'Poetry Workshop', 'Debate Club'], [25, 68, 35, 82, 11];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Abigail Martinez', ['Language Learning Program', 'Science Symposium', 'Music Theory Class', 'Environmental Cleanup', 'Math Competition'], [69, 22, 60, 97, 27];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Andrew Nguyen', ['Robotics Workshop', 'Literature Circle', 'Coding Club', 'Music Recital', 'Health Education Program'], [14, 66, 94, 41, 85];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Barbara Lee', ['STEM Camp', 'Book Club', 'Chess Club', 'Drama Club', 'Language Workshop'], [57, 9, 67, 21, 76];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Christopher Garcia', ['Math Games Competition', 'Film Festival', 'Science Camp', 'Creative Writing Workshop', 'History Lecture Series'], [90, 47, 5, 73, 15];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Elizabeth Taylor', ['Computer Science Competition', 'Book Club', 'Ecology Project', 'Language Workshop', 'Music Recital'], [0, 94, 31, 78, 22];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Daniel Smith', ['Online Course', 'STEM Workshop', 'Robotics Club', 'Science Fair', 'Language Learning'], [62, 3, 48, 86, 96];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Emma Johnson', ['Tutoring Program', 'Virtual Field Trip', 'Mathematics Olympiad', 'Coding Bootcamp', 'Arts Festival'], [30, 87, 14, 51, 98];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Gabriel Brown', ['Environmental Science Project', 'Literacy Program', 'Music Theory Course', 'History Debate Club', 'Health Education Workshop'], [74, 40, 79, 12, 50];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Hannah Williams', ['Coding Club', 'Language Exchange Program', 'Math Tutoring Service', 'Art Class', 'Physics Symposium'], [43, 88, 21, 65, 7];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Isabella Davis', ['Robotics Workshop', 'Virtual Science Lab', 'Writing Club', 'Drama Production', 'Geography Quiz'], [67, 19, 90, 25, 84];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Jacob Wilson', ['STEM Camp', 'Literature Circle', 'Chess Club', 'Poetry Slam', 'Debating Society'], [5, 74, 38, 92, 18];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'James Taylor', ['Computer Science Competition', 'Book Club', 'Ecology Project', 'Language Workshop', 'Music Recital'], [84, 23, 59, 10, 66];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Jennifer Martinez', ['Math Games', 'Film Festival', 'Science Camp', 'Creative Writing Workshop', 'History Lecture Series'], [18, 80, 27, 89, 45];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Joseph Anderson', ['Online Tutoring', 'STEM Conference', 'Robotics Competition', 'Literature Festival', 'Language Exchange'], [75, 37, 61, 18, 91];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Karen Thompson', ['Mathematics Club', 'Virtual Science Fair', 'Writing Workshop', 'Theater Production', 'Geology Field Trip'], [52, 91, 18, 70, 4];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Kevin Rodriguez', ['Coding Bootcamp', 'Music Ensemble', 'History Seminar', 'Art Exhibition', 'Health Fair'], [97, 29, 76, 8, 58];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Laura Davis', ['STEM Workshop', 'Literacy Program', 'Chess Tournament', 'Poetry Workshop', 'Debate Club'], [31, 93, 34, 77, 2];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Michael Martinez', ['Language Learning Program', 'Science Symposium', 'Music Theory Class', 'Environmental Cleanup', 'Math Competition'], [77, 6, 46, 95, 34];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Nancy Nguyen', ['Robotics Workshop', 'Literature Circle', 'Coding Club', 'Music Recital', 'Health Education Program'], [56, 17, 83, 28, 72];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Olivia Lee', ['STEM Camp', 'Book Club', 'Chess Club', 'Drama Club', 'Language Workshop'], [19, 72, 4, 59, 88];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Richard Garcia', ['Math Games Competition', 'Film Festival', 'Science Camp', 'Creative Writing Workshop', 'History Lecture Series'], [73, 44, 10, 76, 20];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Samantha Taylor', ['Computer Science Competition', 'Book Club', 'Ecology Project', 'Language Workshop', 'Music Recital'], [6, 85, 33, 15, 63];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Thomas Anderson', ['Online Course', 'STEM Workshop', 'Robotics Club', 'Science Fair', 'Language Learning'], [39, 1, 50, 88, 99];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Victoria Thompson', ['Tutoring Program', 'Virtual Field Trip', 'Mathematics Olympiad', 'Coding Bootcamp', 'Arts Festival'], [91, 46, 19, 64, 100];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'William Brown', ['Environmental Science Project', 'Literacy Program', 'Music Theory Course', 'History Debate Club', 'Health Education Workshop'], [54, 95, 32, 80, 13];

INSERT INTO CUSTOMERS_ENGAGEMENT_DB.CUSTOMERS_ENGAGEMENT_S.CUSTOMER_ENGAGEMENT (CUSTOMER, PROJECT_TYPES, NUMBER_ACTIVE_PROJECT_TYPE)
SELECT 'Zoe Williams', ['Coding Club', 'Language Exchange Program', 'Math Tutoring Service', 'Art Class', 'Physics Symposium'], [10, 53, 72, 3, 69];
```