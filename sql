CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nfc_id` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `type` enum('student','professor','assistant_professor','associate_professor') NOT NULL,
  `dept` enum('AI&DS','AI&ML','ECE','CSE','EEE') NOT NULL,
  `year` tinyint(1) DEFAULT NULL,
  `semester` tinyint(1) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `nfc_id` (`nfc_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `notices` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `notice_type` enum('event','announcement','staff','student') NOT NULL,
  `dept` enum('AI&DS','AI&ML','ECE','CSE','EEE') NOT NULL,
  `name` varchar(255) NOT NULL,
  `image_path` varchar(255) NOT NULL,
  `from_date` date NOT NULL,
  `to_date` date NOT NULL,
  `year` tinyint(1) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `attendances` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nfc_id` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `time_recorded` datetime NOT NULL,
  `date` date NOT NULL,
  `month` tinyint(2) NOT NULL,
  `day` tinyint(2) NOT NULL,
  `flag` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_active_attendance` (`nfc_id`, `flag`),
  KEY `date_flag` (`date`, `flag`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `attendances_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
