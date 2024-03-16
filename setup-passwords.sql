-- Password Management
DROP PROCEDURE IF EXISTS sp_add_user;
DROP TABLE IF EXISTS user_info;

-- This function generates a specified number of characters for using as a
-- salt in passwords.
DELIMITER !
CREATE FUNCTION make_salt(num_chars INT)
RETURNS VARCHAR(20) DETERMINISTIC
BEGIN
    DECLARE salt VARCHAR(20) DEFAULT '';

    -- Don't want to generate more than 20 characters of salt.
    SET num_chars = LEAST(20, num_chars);

    -- Generate the salt!  Characters used are ASCII code 32 (space)
    -- through 126 ('z').
    WHILE num_chars > 0 DO
        SET salt = CONCAT(salt, CHAR(32 + FLOOR(RAND() * 95)));
        SET num_chars = num_chars - 1;
    END WHILE;

    RETURN salt;
END !
DELIMITER ;

-- This table holds information for authenticating users based on
-- a password, and whether or not the user is an admin.  Passwords
-- are not stored plaintext so that they cannot be used by people that
-- shouldn't have them.
CREATE TABLE user_info (
    -- Usernames are up to 20 characters.
    username VARCHAR(20) PRIMARY KEY,

    -- Salt will be 8 characters all the time, so we can make this 8.
    salt CHAR(8) NOT NULL,

    -- We use SHA-2 with 256-bit hashes.
    password_hash BINARY(64) NOT NULL
);

-- Adds a new user to the user_info table, using the specified password (max
-- of 20 characters). Salts the password with a newly-generated salt value,
-- and then the salt and hash values are both stored in the table.
DELIMITER !
CREATE PROCEDURE sp_add_user(new_username VARCHAR(20), password VARCHAR(20))
BEGIN
  -- Sets up the salt to be used in the password
  DECLARE salt CHAR(8);
  SET salt = make_salt(8);
  -- Inserts new user into user_info table, assumes the username is unique
  INSERT INTO user_info
    VALUES (new_username, salt, SHA2(CONCAT(salt, password), 256));
END !
DELIMITER ;

-- Authenticates the specified username and password against the data
-- in the user_info table.  Returns 1 if the user appears in the table, and the
-- specified password hashes to the value for the user. Otherwise returns 0.
DELIMITER !
CREATE FUNCTION authenticate(username VARCHAR(20), password VARCHAR(20))
RETURNS TINYINT DETERMINISTIC
BEGIN
  -- Salt and password_hash variables used to autheticate the user
  DECLARE salt CHAR(8);
  DECLARE password_hash BINARY(64);
  -- Check to see if the username is valid
  IF username NOT IN (SELECT username FROM user_info) THEN
    RETURN 0;
  END IF;
  -- Stores the correct hashed password for the user
  SELECT u.salt, u.password_hash INTO salt, password_hash
  FROM user_info u
  WHERE u.username = username;
  -- Check to see if the password is correct
  IF SHA2(CONCAT(salt, password), 256) = password_hash THEN
    RETURN 1;
  ELSE
    RETURN 0;
  END IF;
END !
DELIMITER ;

-- Create a procedure sp_change_password to generate a new salt and change the given
-- user's password to the given password (after salting and hashing)
DELIMITER !
CREATE PROCEDURE sp_change_password(
  username VARCHAR(20),
  new_password VARCHAR(20)
)
BEGIN
  -- Sets up the salt for the new password
  DECLARE new_salt CHAR(8);
  SET new_salt = make_salt(8);
  -- Updates the password of the user in user_info table
  UPDATE user_info
  SET
    salt = new_salt,
    password_hash = SHA2(CONCAT(salt, new_password), 256)
  WHERE user_info.username = username;
END !
DELIMITER ;