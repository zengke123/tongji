/*
Navicat MySQL Data Transfer

Source Server         : root
Source Server Version : 50721
Source Host           : localhost:3306
Source Database       : tongji

Target Server Type    : MYSQL
Target Server Version : 50721
File Encoding         : 65001

Date: 2018-07-11 12:51:00
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for caps
-- ----------------------------
DROP TABLE IF EXISTS `caps`;
CREATE TABLE `caps` (
  `date` varchar(32) NOT NULL,
  `scp_caps` float(7,2) DEFAULT NULL,
  `scpas_caps` float(7,2) DEFAULT NULL,
  `catas_caps` float(7,2) DEFAULT NULL,
  PRIMARY KEY (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
CREATE INDEX date_idx on caps(date);

-- ----------------------------
-- Records of caps
-- ----------------------------
INSERT INTO `caps` VALUES ('20180614', '1246.38', '3437.24','913.73');
INSERT INTO `caps` VALUES ('20180615', '1295.23', '3513.78','977.77');
INSERT INTO `caps` VALUES ('20180616', '1197.66', '2959.71','732.45');
INSERT INTO `caps` VALUES ('20180617', '1192.02', '2817.25','742.32');
INSERT INTO `caps` VALUES ('20180618', '1260.46', '2734.63','668.27');
INSERT INTO `caps` VALUES ('20180619', '1274.01', '5331.57','914.85');
INSERT INTO `caps` VALUES ('20180620', '1243.14', '5300.06','937.15');
INSERT INTO `caps` VALUES ('20180621', '1241.47', '3463.7','1007.66');
INSERT INTO `caps` VALUES ('20180622', '1261.17', '3656.46','787.47');
INSERT INTO `caps` VALUES ('20180623', '1196.47', '3196.52','691.9');
INSERT INTO `caps` VALUES ('20180624', '1086.22', '2857.66','619.75');
INSERT INTO `caps` VALUES ('20180625', '1284.36', '3753.15','803.62');
INSERT INTO `caps` VALUES ('20180626', '1284.38', '3720.4','799.69');
INSERT INTO `caps` VALUES ('20180627', '1283.03', '3703.87','797.46');
INSERT INTO `caps` VALUES ('20180628', '1292.21', '3702.95','794.82');
INSERT INTO `caps` VALUES ('20180629', '1299.19', '3771.7','806.43');
INSERT INTO `caps` VALUES ('20180630', '1175.16', '3179.95','687.49');
INSERT INTO `caps` VALUES ('20180701', '1114.79', '2956.18','631.73');
INSERT INTO `caps` VALUES ('20180702', '1318.09', '3741.91','785.12');
INSERT INTO `caps` VALUES ('20180703', '1302.38', '3743.95','795.87');
INSERT INTO `caps` VALUES ('20180704', '1300.46', '3723.64','793.69');
INSERT INTO `caps` VALUES ('20180705', '1301.72', '3745.72','805.92');
INSERT INTO `caps` VALUES ('20180706', '1299.02', '3757.64','803.8');
INSERT INTO `caps` VALUES ('20180707', '1124.32', '3046.66','656.92');
INSERT INTO `caps` VALUES ('20180708', '1073', '2858.98','612.81');
INSERT INTO `caps` VALUES ('20180709', '1248.73', '3603.1','775.13');

ALTER TABLE caps ADD COLUMN vrbt_caps float(7,2) DEFAULT NULL;