-- phpMyAdmin SQL Dump
-- version 4.5.1
-- http://www.phpmyadmin.net
--
-- Host: 127.0.0.1
-- Generation Time: Feb 15, 2018 at 07:18 AM
-- Server version: 10.1.16-MariaDB
-- PHP Version: 5.6.24

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `flaskdb`
--

-- --------------------------------------------------------

--
-- Table structure for table `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('bdee7da66470');

-- --------------------------------------------------------

--
-- Table structure for table `followers`
--

CREATE TABLE `followers` (
  `follower_id` int(11) DEFAULT NULL,
  `followed_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `followers`
--

INSERT INTO `followers` (`follower_id`, `followed_id`) VALUES
(3, 1),
(1, 3),
(4, 3),
(4, 1),
(4, 2),
(1, 2);

-- --------------------------------------------------------

--
-- Table structure for table `post`
--

CREATE TABLE `post` (
  `id` int(11) NOT NULL,
  `body` varchar(180) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `post`
--

INSERT INTO `post` (`id`, `body`, `timestamp`, `user_id`) VALUES
(1, 'Hi, this is after integration of mysql server. Goodbye old sqlite :)', '2018-02-11 17:11:18', 1),
(2, 'whatsup peepal', '2018-02-11 17:24:57', 2),
(3, 'why is the username not clickable in the explore and home pages ?', '2018-02-11 17:38:00', 2),
(4, 'bow wou guys, i like to sleep and eat', '2018-02-11 17:45:26', 3),
(5, '@asthabatra, corrected the bug. Hi bruno, i miss u', '2018-02-11 17:59:42', 1),
(6, '@sanskarssh\r\nbow wou master, i miss u too', '2018-02-11 18:06:57', 3),
(7, 'Hi bruh, nice place this. @brunojnr brunooooooooooo :*', '2018-02-11 18:12:28', 4);

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `username` varchar(64) DEFAULT NULL,
  `email` varchar(120) DEFAULT NULL,
  `password_hash` varchar(128) DEFAULT NULL,
  `about_me` varchar(180) DEFAULT NULL,
  `last_seen` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `username`, `email`, `password_hash`, `about_me`, `last_seen`) VALUES
(1, 'sanskarssh', 'sanskar2996@gmail.com', 'pbkdf2:sha256:50000$xCGuUWqn$b57c3174ab927aacae37c147db460462b8bffc193cc713b4cbb597f8dc955bef', '# official sanskar.\r\nI am the boss here.', '2018-02-14 20:24:53'),
(2, 'asthabatra', 'batra.astha27@gmail.com', 'pbkdf2:sha256:50000$J82e6nxB$dc4f399ea081b6abd779c627539edf79d7ef11904570c8d45b2429b91689ff45', '#versatile', '2018-02-11 17:38:03'),
(3, 'Bruno Jr. ', 'golu.s29@gmail.com', 'pbkdf2:sha256:50000$uMxMCt1N$16ac5adafacced5518850186e863661982ffafc708fe03811fef4977d5fc68d3', 'bow wou. i was the best dog. golu misses me alot', '2018-02-11 18:08:29'),
(4, 'shubhisharma211', 'shubhisharma211@gmail.com', 'pbkdf2:sha256:50000$O6QACgqu$6c0acb7de3fa81849df4aebcce3073b4c0d2832d55798cb8c20e087043ecbc9e', NULL, '2018-02-11 18:13:26');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- Indexes for table `followers`
--
ALTER TABLE `followers`
  ADD KEY `followed_id` (`followed_id`),
  ADD KEY `follower_id` (`follower_id`);

--
-- Indexes for table `post`
--
ALTER TABLE `post`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `ix_post_timestamp` (`timestamp`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_user_email` (`email`),
  ADD UNIQUE KEY `ix_user_username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `post`
--
ALTER TABLE `post`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;
--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
--
-- Constraints for dumped tables
--

--
-- Constraints for table `followers`
--
ALTER TABLE `followers`
  ADD CONSTRAINT `followers_ibfk_1` FOREIGN KEY (`followed_id`) REFERENCES `user` (`id`),
  ADD CONSTRAINT `followers_ibfk_2` FOREIGN KEY (`follower_id`) REFERENCES `user` (`id`);

--
-- Constraints for table `post`
--
ALTER TABLE `post`
  ADD CONSTRAINT `post_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
