SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;
REGISTER ../lib/porky-abbreviated.jar;
REGISTER ../lib/webarchive-commons-1.1.7.jar;

-- This is how you would call out a to a python script with a designated function if you wanted to.

REGISTER 'padding_udfs.py' USING jython AS paddingfuncs;

-- This flips the URL back to front so the important parts are at the beginning e.g. gov.whitehouse.frontpage......
-- I haven't really figured out why this is helpful, but it does help with using existing scripts because the
-- ones internet archive wrote use this format

DEFINE SURTURL org.archive.porky.SurtUrlKey();
DEFINE pad_str paddingfuncs.pad_string();


Archive = LOAD '/user/lucylin/arcs/bucket-0/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance0 = FOREACH Archive GENERATE URL AS URLs,
                                     surt AS surt,
                                     checksum AS checksum,
                                     date AS date,
                                     code AS code,
                                     title AS title,
                                     description AS description,
                                     pad_str(content);

Archive = LOAD '/user/lucylin/arcs/bucket-1/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance1 = FOREACH Archive GENERATE URL AS URLs,
                                     surt AS surt,
                                     checksum AS checksum,
                                     date AS date,
                                     code AS code,
                                     title AS title,
                                     description AS description,
                                     pad_str(content);

Archive = LOAD '/user/lucylin/arcs/bucket-2/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance2 = FOREACH Archive GENERATE URL AS URLs,
                                     surt AS surt,
                                     checksum AS checksum,
                                     date AS date,
                                     code AS code,
                                     title AS title,
                                     description AS description,
                                     pad_str(content);

Archive = LOAD '/user/lucylin/arcs/bucket-3/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance3 = FOREACH Archive GENERATE URL AS URLs,
                                     surt AS surt,
                                     checksum AS checksum,
                                     date AS date,
                                     code AS code,
                                     title AS title,
                                     description AS description,
                                     pad_str(content);

Archive = LOAD '/user/lucylin/arcs/bucket-4/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance4 = FOREACH Archive GENERATE URL AS URLs,
                                     surt AS surt,
                                     checksum AS checksum,
                                     date AS date,
                                     code AS code,
                                     title AS title,
                                     description AS description,
                                     pad_str(content);

Archive = LOAD '/user/lucylin/arcs/bucket-5/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance5 = FOREACH Archive GENERATE URL AS URLs,
                                     surt AS surt,
                                     checksum AS checksum,
                                     date AS date,
                                     code AS code,
                                     title AS title,
                                     description AS description,
                                     pad_str(content);

Archive = LOAD '/user/lucylin/warcs/bucket-0/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance0w = FOREACH Archive GENERATE URL AS URLs,
                                     surt AS surt,
                                     checksum AS checksum,
                                     date AS date,
                                     code AS code,
                                     title AS title,
                                     description AS description,
                                     pad_str(content);

Archive = LOAD '/user/lucylin/warcs/bucket-1/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance1w = FOREACH Archive GENERATE URL AS URLs,
                                     surt AS surt,
                                     checksum AS checksum,
                                     date AS date,
                                     code AS code,
                                     title AS title,
                                     description AS description,
                                     pad_str(content);

Archive = LOAD '/user/lucylin/warcs/bucket-2/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance2w = FOREACH Archive GENERATE URL AS URLs,
                                     surt AS surt,
                                     checksum AS checksum,
                                     date AS date,
                                     code AS code,
                                     title AS title,
                                     description AS description,
                                     pad_str(content);

instance = UNION instance0, instance1, instance2, instance3, instance4, instance5, instance0w, instance1w, instance2w;

religious_instance = FILTER instance BY document MATCHES '.*[^a-z](fundamentalism|interreligion|interreligions|ecclesiastic|ecclesiastical|afterlives|episcopalian|episcopalians|episcopals|irreligion|pentecosts|proselytize|proselytise|proselytism|proselytization|proselytizer|proselytizers|proselytiser|proselytisers|proselyte)[^a-z].*'
OR document MATCHES '.*[^a-z](proselytes|proselytized|proselytizes|proselytizing|proselytised|proselytises|proselytising|salvations|hashana|hashanah|mujahid|mujahideen|puritans|puritanical|religions|religious|sanctify|sanctified|sanctifies|sanctifying)[^a-z].*'
OR document MATCHES '.*[^a-z](sanctification|worships|worshiped|worshipped|worshiping|worshipping|biblically|forsake|forsaken|forsaking|rabbinical|miracles|zionist|zionism|judah|judas|ministry|god|spirit|temple)[^a-z].*'
OR document MATCHES '.*[^a-z](bishop|paradise|gospel|methodist|missionary|faith|angel|religion|mercy|chapel|heaven|prayer|baptist|shrine|immoral|veil|rabbi|worship|chaplain|sin)[^a-z].*'
OR document MATCHES '.*[^a-z](bible|mosque|sacred|protestant|presbyterian|moral|pagan|church|sinner|morality|zion|jewish|belief|muslim|minister|passover|pope|rite|satan|lutheran)[^a-z].*'
OR document MATCHES '.*[^a-z](meditate|islam|jesus|christmas|sectarian|lord|saint|goddess|hellish|sacrifice|fundamentalist|devil|vatican|sikh|soul|divine|preach|ritual|pastor|catholic)[^a-z].*'
OR document MATCHES '.*[^a-z](orthodox|testament|clergy|demons|morals|nun|monk|bless|sunni|priest|hells|mecca|christ|holy|sabbath|pew|altar|pilgrim|shia|imam)[^a-z].*'
OR document MATCHES '.*[^a-z](amen|jew|penance|prophet|mennonite|hymn|yiddish|mohammad|scripture|confess|sect|demon|amish|shiite|holiest|christen|buddha|mormon|muhammed|angelic)[^a-z].*'
OR document MATCHES '.*[^a-z](theology|pentecost|immortal|hindu|papal|angels|kosher|rosary|episcopal|baptize|christain|allah|jesuit|alla|pious|koran|puritan|seminary|mitzvah|convents)[^a-z].*'
OR document MATCHES '.*[^a-z](quran|kippur|afterlife|piet|karma|zen|crucify|torah|gentile|ramadan|demonic|juda|holier|evangelic|monastry|kingdom|mass|spiritual|devine|exodus)[^a-z].*'
OR document MATCHES '.*[^a-z](catholics|scriptures|christian|quaker|saints|dios|hell|halo|cardinal|eternity|revelations|vigil|holiness|pontifical|redemption|sacredness|theological|spirituality|christians|evangelist)[^a-z].*'
OR document MATCHES '.*[^a-z](flock|glory|vestments|lent|sins|preaching|pray|micah|emmanuel|ministers|sanctuaries|godly|vicar|ministries|conversions|evangelical|evil|nuns|monks|lazarus)[^a-z].*'
OR document MATCHES '.*[^a-z](heavenly|moses|rites|fellowship|congregation|fundamentalists|crusade|churches|preaches|sanctity|biblical|genesis|baptists|bibles|serpent|reverend|preachers|archbishop|easter|pastors)[^a-z].*'
OR document MATCHES '.*[^a-z](creed|crucifix|believers|commandment|congregations|pulpit|covenant|samaritan|prophets|revelation|monastery|missionaries|monotheistic|parish|ezekiel|salvation|sinful|crusader|christianity|diocesan)[^a-z].*'
OR document MATCHES '.*[^a-z](diocese|prophesy|pentecostal|denominations|sects|glorious|monsignor|archdiocese|psalmist|communion|apostle|gabriel|preached|christened|faithfuls|popes|psalm|nehemiah|disciples|seminaries)[^a-z].*'
OR document MATCHES '.*[^a-z](testaments|deacon|creator|exalted|ishmael|dioceses|redeemer|denomination|ministership|martyrs|preacher|cathedral|leviticus|spiritually|godspeed|evangelicals|devout|unholy|adventists|prophesied)[^a-z].*'
OR document MATCHES '.*[^a-z](savior|sermon|pontiff|priests|proverb|ephesians|prophecies|spirituals|christening|monasteries|exaltation|almighty|catholicism|navidad|satanic|agape|psalms|messiah|ungodly|theologian)[^a-z].*'
OR document MATCHES '.*[^a-z](theologically|congregants|ark|clergymen|isaiah|baptism|baptized|priesthood|interreligious|magi|clergyman|theocracy|deity|steeple|messianic|ecclesiastes|convent|canonized|worshiper|worshipers)[^a-z].*'
OR document MATCHES '.*[^a-z](worshipper|worshippers|evangelism|tabernacle|herod|anglicans|coreligionists|israelites|monotheism|sectarianism|vigils|godsend|lucifer|basilica|apostolic|cbn|crucifixion|theocratic|sinned|pharaoh)[^a-z].*'
OR document MATCHES '.*[^a-z](beatitude|epistle|ministered|deuteronomy|prophesized|pews|optimi|pontius|calvinists|espiritual|prophetess|godless|churchyard|seminarian|lenten|corinthians|prayerfully|apostles|repent|atonement)[^a-z].*'
OR document MATCHES '.*[^a-z](pastorate|evildoer|hallelujah|saviour|scriptural|sacrilegious|catholicos|malachi|pieties|pulpits|nazarenes|churchgoing|leviathan|rosaries|pharoah|pietists|exalteth|believeth|parishioner|churchgoer)[^a-z].*'
OR document MATCHES '.*[^a-z](zaccheus|irreligious|relig|reverends|monsignors|galatians|miracle|miraculous|archabbey|baptistries|prophesizing|multisectarian|emmanual|godgiven|archabbot|god-given|arks|deit|doom|gods)[^a-z].*'
OR document MATCHES '.*[^a-z](jews|sinn|amens|dooms|exalt|grace|hymns|imams|piety|prays|rosar|sikhs|souls|veils|wrath|altars|creeds|crucif|devils|dioses)[^a-z].*'
OR document MATCHES '.*[^a-z](doomed|evilly|exalts|faiths|graces|haloes|hindus|karmas|korans|martyr|pagans|prayed|qurans|rabbis|sunnis|vicars|beliefs|bishops|blesses|blessed)[^a-z].*'
OR document MATCHES '.*[^a-z](buddhas|chapels|deacons|deities|devines|devined|easters|eternit|gospels|heavens|jesuits|mormons|mosques|muslims|pietist|praying|prayers|prophec|prophes|quakers)[^a-z].*'
OR document MATCHES '.*[^a-z](repents|saintly|sanctit|saviors|seminar|sermons|shiites|shrines|sinning|sinners|spirits|temples|theolog|agnostic|anglican|baptisms|baptizes|believer|blessing|canonize)[^a-z].*'
OR document MATCHES '.*[^a-z](crusades|devoutly|disciple|divinely|epistles|faithful|gentiles|godsends|merciful|mitzvahs|nazarene|parishes|penances|pharaohs|pharoahs|pilgrims|pontiffs|prophecy|prophesi|proverbs)[^a-z].*'
OR document MATCHES '.*[^a-z](purgator|repented|ritually|sabbaths|sacredly|sanctuar|saviours|serpents|sinfully|steeples|theocrac|vestment|adventist|agnostics|baptistry|basilicas|blessedly|calvinist|canonizes|cardinals)[^a-z].*'
OR document MATCHES '.*[^a-z](chaplains|christens|confesses|confessed|covenants|crucifies|crucified|crusaders|evildoers|goddesses|immorally|israelite|meditates|meditated|navidades|paradises|prayerful|prophesiz|psalmists|purgatory)[^a-z].*'
OR document MATCHES '.*[^a-z](redeemers|repenting|sanctuary|archabbeys|archabbots|atonements|beatitudes|cathedrals|communions|confessing|congregant|conversion|crucifixes|crucifying|eternities|leviathans|mennonites|mercifully|methodists|pastorates)[^a-z].*'
OR document MATCHES '.*[^a-z](prophesies|sacrifices|samaritans|sanctities|theologies|angelically|archbishops|christmases|churchgoers|churchyards|demonically|exaltations|hallelujahs|priesthoods|prophesizes|protestants|purgatories|redemptions|tabernacles|theocracies)[^a-z].*'
OR document MATCHES '.*[^a-z](theologians|archdioceses|commandments|crucifixions|espirituales|parishioners|pontifically|prophetesses|scripturally|coreligionist|theocratically)[^a-z].*';


religious_instance = ORDER religious_instance BY date;

STORE religious_instance INTO 'all_religious_captures2/' USING PigStorage('\t');

religious_instance_no_text = FOREACH religious_instance GENERATE URLs AS URL,
                                                                 surt AS surt,
                                                                 checksum AS checksum,
                                                                 date AS date;

count_religious_instance_pre_checksum = GROUP religious_instance_no_text ALL;

counted_religious_instance_pre_checksum = FOREACH count_religious_instance_pre_checksum GENERATE COUNT(religious_instance_no_text) AS counted;

DUMP counted_religious_instance_pre_checksum;

Checksum = LOAD '$I_CHECKSUM_DATA' USING PigStorage() AS (surt:chararray, date:chararray, checksum:chararray);

all_entries = JOIN religious_instance_no_text BY (surt, checksum), Checksum BY (surt, checksum);

all_entries = FOREACH all_entries GENERATE Checksum::date AS date,
                                           religious_instance_no_text::URL AS URL,
                                           religious_instance_no_text::surt AS surt,
                                           religious_instance_no_text::checksum AS checksum;

ordered_by_date = ORDER all_entries BY date ASC;

STORE ordered_by_date INTO 'all_dates_religious_only2/' USING PigStorage('\t');

for_counting = GROUP all_entries ALL;

for_counting = FOREACH for_counting GENERATE COUNT(all_entries) AS counted;

DUMP for_counting;