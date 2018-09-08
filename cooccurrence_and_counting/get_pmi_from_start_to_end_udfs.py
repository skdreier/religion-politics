# I didn't get around to making this a template, but the only things to change for a different
# set of keywords would be lines 10-21. Everything else would stay the same.

import re

# if some religious terms contain others, make sure that the ones
# that are a substring of another come AFTER the longer term
# containing it, in the same batch of regexes

regexes_to_search_for = [
    re.compile('(?:god-given)|(?:ark)|(?:cbn)|(?:god)|(?:jew)|(?:nun)|(?:pew)|(?:sin)|(?:zen)|(?:alla)|(?:amen)|(?:arks)|(?:deit)|(?:dios)|(?:doom)|(?:evil)|(?:gods)|(?:halo)|(?:hell)|(?:holy)|(?:hymn)|(?:imam)|(?:jews)|(?:juda)|(?:lent)|(?:lord)|(?:magi)|(?:monk)|(?:nuns)|(?:pews)|(?:piet)|(?:pope)|(?:pray)|(?:rite)|(?:sect)|(?:shia)|(?:sikh)|(?:sinn)|(?:sins)|(?:soul)|(?:veil)|(?:zion)|(?:agape)|(?:allah)|(?:altar)|(?:amens)|(?:amish)|(?:angel)|(?:bible)|(?:bless)|(?:creed)|(?:deity)|(?:demon)|(?:devil)|(?:dooms)|(?:exalt)|(?:flock)|(?:godly)|(?:hells)|(?:herod)|(?:hindu)|(?:hymns)|(?:imams)|(?:islam)|(?:jesus)|(?:judah)|(?:judas)|(?:karma)|(?:koran)|(?:mecca)|(?:mercy)|(?:micah)|(?:monks)|(?:moral)|(?:moses)|(?:pagan)|(?:papal)|(?:piety)|(?:pious)|(?:popes)|(?:prays)|(?:psalm)|(?:quran)|(?:rabbi)|(?:relig)|(?:rites)|(?:rosar)|(?:saint)|(?:satan)|(?:sects)|(?:sikhs)|(?:souls)|(?:sunni)|(?:torah)|(?:veils)|(?:vicar)|(?:vigil)|(?:wrath)|(?:altars)|(?:belief)|(?:bibles)|(?:buddha)'),
    re.compile('(?:chapel)|(?:christ)|(?:clergy)|(?:creeds)|(?:crucif)|(?:deacon)|(?:demons)|(?:devils)|(?:devine)|(?:devout)|(?:dioses)|(?:divine)|(?:doomed)|(?:easter)|(?:evilly)|(?:exalts)|(?:exodus)|(?:faiths)|(?:gospel)|(?:graces)|(?:haloes)|(?:hindus)|(?:holier)|(?:isaiah)|(?:jesuit)|(?:jewish)|(?:karmas)|(?:kippur)|(?:korans)|(?:kosher)|(?:lenten)|(?:martyr)|(?:morals)|(?:mormon)|(?:mosque)|(?:muslim)|(?:optimi)|(?:pagans)|(?:parish)|(?:prayed)|(?:prayer)|(?:preach)|(?:priest)|(?:psalms)|(?:pulpit)|(?:quaker)|(?:qurans)|(?:rabbis)|(?:repent)|(?:ritual)|(?:rosary)|(?:sacred)|(?:saints)|(?:savior)|(?:sermon)|(?:shiite)|(?:shrine)|(?:sinful)|(?:sinned)|(?:sinner)|(?:sunnis)|(?:unholy)|(?:vicars)|(?:vigils)|(?:angelic)|(?:apostle)|(?:baptism)|(?:baptist)|(?:baptize)|(?:beliefs)|(?:bishops)|(?:blessed)|(?:blesses)|(?:buddhas)|(?:chapels)|(?:confess)|(?:convent)|(?:creator)|(?:crucify)|(?:crusade)|(?:deacons)|(?:deities)|(?:demonic)|(?:devined)|(?:devines)|(?:diocese)|(?:easters)|(?:epistle)|(?:eternit)|(?:exalted)|(?:ezekiel)|(?:forsake)|(?:gabriel)|(?:genesis)|(?:gentile)|(?:goddess)|(?:godless)|(?:godsend)|(?:gospels)|(?:hashana)|(?:heavens)|(?:hellish)'),
    re.compile('(?:holiest)|(?:immoral)|(?:ishmael)|(?:jesuits)|(?:lazarus)|(?:lucifer)|(?:malachi)|(?:martyrs)|(?:messiah)|(?:miracle)|(?:mitzvah)|(?:mormons)|(?:mosques)|(?:mujahid)|(?:muslims)|(?:navidad)|(?:pastors)|(?:penance)|(?:pharaoh)|(?:pharoah)|(?:pieties)|(?:pietist)|(?:pilgrim)|(?:pontiff)|(?:pontius)|(?:prayers)|(?:praying)|(?:priests)|(?:prophec)|(?:prophes)|(?:prophet)|(?:proverb)|(?:pulpits)|(?:puritan)|(?:quakers)|(?:ramadan)|(?:repents)|(?:sabbath)|(?:saintly)|(?:sanctit)|(?:satanic)|(?:saviors)|(?:saviour)|(?:sermons)|(?:serpent)|(?:shiites)|(?:shrines)|(?:sinners)|(?:sinning)|(?:spirits)|(?:steeple)|(?:temples)|(?:theolog)|(?:ungodly)|(?:vatican)|(?:worship)|(?:yiddish)|(?:zionism)|(?:zionist)|(?:agnostic)|(?:almighty)|(?:anglican)|(?:apostles)|(?:baptisms)|(?:baptists)|(?:baptized)|(?:baptizes)|(?:basilica)|(?:believer)|(?:biblical)|(?:blessing)|(?:canonize)|(?:cardinal)|(?:catholic)|(?:chaplain)|(?:christen)|(?:churches)|(?:convents)|(?:covenant)|(?:crucifix)|(?:crusader)|(?:crusades)|(?:devoutly)|(?:diocesan)|(?:dioceses)|(?:disciple)|(?:divinely)|(?:emmanual)|(?:emmanuel)|(?:epistles)|(?:eternity)|(?:evildoer)|(?:exalteth)|(?:forsaken)|(?:gentiles)|(?:glorious)|(?:godgiven)|(?:godsends)|(?:godspeed)|(?:hashanah)|(?:heavenly)'),
    re.compile('(?:holiness)|(?:immortal)|(?:lutheran)|(?:meditate)|(?:merciful)|(?:ministry)|(?:miracles)|(?:mitzvahs)|(?:mohammad)|(?:monastry)|(?:morality)|(?:muhammed)|(?:nazarene)|(?:nehemiah)|(?:orthodox)|(?:paradise)|(?:parishes)|(?:passover)|(?:penances)|(?:pharaohs)|(?:pharoahs)|(?:pietists)|(?:pilgrims)|(?:pontiffs)|(?:preached)|(?:preacher)|(?:preaches)|(?:prophecy)|(?:prophesi)|(?:prophesy)|(?:prophets)|(?:proverbs)|(?:psalmist)|(?:purgator)|(?:puritans)|(?:redeemer)|(?:religion)|(?:repented)|(?:reverend)|(?:ritually)|(?:rosaries)|(?:sabbaths)|(?:sacredly)|(?:sanctify)|(?:sanctity)|(?:sanctuar)|(?:saviours)|(?:seminary)|(?:serpents)|(?:sinfully)|(?:steeples)|(?:theocrac)|(?:theology)|(?:vestment)|(?:worships)|(?:zaccheus)|(?:adventist)|(?:afterlife)|(?:agnostics)|(?:anglicans)|(?:apostolic)|(?:archabbey)|(?:archabbot)|(?:atonement)|(?:baptistry)|(?:basilicas)|(?:beatitude)|(?:believeth)|(?:blessedly)|(?:calvinist)|(?:canonized)|(?:canonizes)|(?:cardinals)|(?:cathedral)|(?:catholics)|(?:chaplains)|(?:christain)|(?:christens)|(?:christmas)|(?:clergyman)|(?:clergymen)|(?:communion)|(?:confessed)|(?:confesses)|(?:covenants)|(?:crucified)|(?:crucifies)|(?:crusaders)|(?:disciples)|(?:ephesians)|(?:episcopal)|(?:evangelic)|(?:evildoers)|(?:faithfuls)|(?:forsaking)|(?:galatians)|(?:goddesses)|(?:immorally)|(?:israelite)|(?:leviathan)|(?:leviticus)|(?:meditated)'),
    re.compile('(?:meditates)|(?:mennonite)|(?:messianic)|(?:methodist)|(?:monastery)|(?:monsignor)|(?:navidades)|(?:nazarenes)|(?:paradises)|(?:pastorate)|(?:pentecost)|(?:prayerful)|(?:preachers)|(?:preaching)|(?:prophesiz)|(?:proselyte)|(?:psalmists)|(?:purgatory)|(?:redeemers)|(?:religions)|(?:religious)|(?:repenting)|(?:reverends)|(?:sacrifice)|(?:salvation)|(?:samaritan)|(?:scripture)|(?:sectarian)|(?:spiritual)|(?:theocracy)|(?:vestments)|(?:worshiped)|(?:worshiper)|(?:adventists)|(?:afterlives)|(?:archabbeys)|(?:archabbots)|(?:archbishop)|(?:atonements)|(?:beatitudes)|(?:biblically)|(?:calvinists)|(?:cathedrals)|(?:catholicos)|(?:christened)|(?:christians)|(?:churchgoer)|(?:churchyard)|(?:communions)|(?:confessing)|(?:congregant)|(?:conversion)|(?:crucifixes)|(?:crucifying)|(?:episcopals)|(?:espiritual)|(?:eternities)|(?:evangelism)|(?:evangelist)|(?:exaltation)|(?:hallelujah)|(?:irreligion)|(?:israelites)|(?:leviathans)|(?:mennonites)|(?:mercifully)|(?:methodists)|(?:ministered)|(?:ministries)|(?:miraculous)|(?:missionary)|(?:monotheism)|(?:monsignors)|(?:mujahideen)|(?:pastorates)|(?:pentecosts)|(?:pontifical)|(?:priesthood)|(?:prophecies)|(?:prophesied)|(?:prophesies)|(?:prophetess)|(?:proselytes)|(?:protestant)|(?:rabbinical)|(?:redemption)|(?:revelation)|(?:sacredness)|(?:sacrifices)|(?:salvations)|(?:samaritans)|(?:sanctified)|(?:sanctifies)|(?:sanctities)|(?:scriptural)|(?:scriptures)|(?:seminarian)|(?:seminaries)|(?:spirituals)|(?:tabernacle)|(?:testaments)'),
    re.compile('(?:theocratic)|(?:theologian)|(?:theologies)|(?:worshipers)|(?:worshiping)|(?:worshipped)|(?:worshipper)|(?:angelically)|(?:archbishops)|(?:archdiocese)|(?:baptistries)|(?:catholicism)|(?:christening)|(?:christmases)|(?:churchgoers)|(?:churchgoing)|(?:churchyards)|(?:commandment)|(?:congregants)|(?:conversions)|(?:corinthians)|(?:crucifixion)|(?:demonically)|(?:deuteronomy)|(?:evangelical)|(?:exaltations)|(?:hallelujahs)|(?:irreligious)|(?:monasteries)|(?:parishioner)|(?:pentecostal)|(?:prayerfully)|(?:priesthoods)|(?:prophesized)|(?:prophesizes)|(?:proselytise)|(?:proselytism)|(?:proselytize)|(?:protestants)|(?:purgatories)|(?:puritanical)|(?:redemptions)|(?:revelations)|(?:sanctifying)|(?:spiritually)|(?:tabernacles)|(?:theocracies)|(?:theologians)|(?:theological)|(?:worshippers)|(?:worshipping)|(?:archdioceses)|(?:christianity)|(?:commandments)|(?:congregation)|(?:crucifixions)|(?:denomination)|(?:ecclesiastes)|(?:ecclesiastic)|(?:episcopalian)|(?:espirituales)|(?:evangelicals)|(?:ministership)|(?:missionaries)|(?:monotheistic)|(?:parishioners)|(?:pontifically)|(?:presbyterian)|(?:prophesizing)|(?:prophetesses)|(?:proselytised)|(?:proselytiser)|(?:proselytises)|(?:proselytized)|(?:proselytizer)|(?:proselytizes)|(?:sacrilegious)|(?:scripturally)|(?:sectarianism)|(?:spirituality)|(?:congregations)|(?:coreligionist)|(?:denominations)|(?:episcopalians)|(?:interreligion)|(?:proselytisers)|(?:proselytising)|(?:proselytizers)|(?:proselytizing)|(?:theologically)|(?:coreligionists)|(?:ecclesiastical)|(?:fundamentalism)|(?:fundamentalist)|(?:interreligions)|(?:interreligious)|(?:multisectarian)|(?:sanctification)|(?:theocratically)|(?:fundamentalists)|(?:proselytization)'),
    re.compile('(?:sanctuaries)|(?:ministers)|(?:sanctuary)|(?:testament)|(?:fellowship)|(?:mass)|(?:faith)|(?:glory)|(?:grace)|(?:angels)|(?:bishop)|(?:church)|(?:heaven)|(?:pastor)|(?:spirit)|(?:temple)|(?:kingdom)|(?:faithful)|(?:minister)|(?:believers)|(?:christian)')
]


regexes_to_consider_false_matches = re.compile('(?:congresswoman grace napolitano)|(?:ministers of foreign affairs)|(?:weapons of mass destruction)|(?:minister of foreign affairs)|(?:weapon of mass destruction)|(?:spirit of bipartisanship)|(?:congressional fellowship)|(?:good faith negotiations)|(?:matches made in heaven)|(?:full faith and credit)|(?:spirit of cooperation)|(?:match made in heaven)|(?:spirit of bipartisan)|(?:wildlife sanctuaries)|(?:mass communications)|(?:angels in adoption)|(?:congressman bishop)|(?:spirit of commerce)|(?:wildlife sanctuary)|(?:marine sanctuaries)|(?:good faith effort)|(?:napolitano, grace)|(?:sanford d\\. bishop)|(?:christian kennedy)|(?:temple lake park)|(?:strong believers)|(?:marine sanctuary)|(?:prime ministers)|(?:weight or mass)|(?:united kingdom)|(?:animal kingdom)|(?:party faithful)|(?:prime minister)|(?:a testament to)|(?:church street)|(?:mass transit)|(?:former glory)|(?:jeff bishop)|(?:bill pastor)|(?:rob bishop)|(?:mr\\. bishop)|(?:rep grace)|(?:church st)|(?:bishop\\.0)|(?:bishop\\.1)|(?:bishop\\.2)|(?:bishop\\.3)|(?:bishop\\.4)|(?:bishop\\.5)|(?:bishop\\.6)|(?:bishop\\.7)|(?:bishop\\.8)|(?:bishop\\.9)|(?:d-mass)|(?:r-mass)')


@outputSchema("bag{tuple(searchterm:chararray, text:chararray)}")
def docmakingudf(text):
    placeholder_str = '``````````````'
    try:
        text = text.decode('utf-8')
    except:
        text = str(text).strip()
        if text == '' or text == "None":
            return []

    false_match_inds = [(m.start(0), m.end(0)) for m in regexes_to_consider_false_matches.finditer(text)]
    match_start_end_inds = []
    for regex_to_search_for in regexes_to_search_for:
        new_inds = [(m.start(0), m.end(0)) for m in regex_to_search_for.finditer(text)]
        for i in range(len(new_inds) - 1, -1, -1):
            if text[new_inds[i][0] - 1].isalpha() or text[new_inds[i][1]].isalpha():
                del new_inds[i]
        inds_to_del = []
        for i in range(len(new_inds) - 1, -1, -1):
            for j in range(len(false_match_inds)):
                #assert i < len(new_inds), text
                if new_inds[i][0] >= false_match_inds[j][0] and new_inds[i][1] <= false_match_inds[j][1]:
                    inds_to_del.append(i)  # it's a false match
        for ind in inds_to_del:
            del new_inds[ind]
        new_list_pointer = 0
        big_list_pointer = 0
        while new_list_pointer < len(new_inds):
            if big_list_pointer >= len(match_start_end_inds):
                while new_list_pointer < len(new_inds):
                    match_start_end_inds.append(new_inds[new_list_pointer])
                    new_list_pointer += 1
                break
            else:
                if match_start_end_inds[big_list_pointer][0] >= new_inds[new_list_pointer][0]:
                    match_start_end_inds.insert(big_list_pointer, new_inds[new_list_pointer])
                    new_list_pointer += 1
            big_list_pointer += 1
    bag_to_return = []
    if len(match_start_end_inds) == 0:
        return bag_to_return
    string_matches = []
    for match_ind in range(len(match_start_end_inds) - 1, -1, -1):
        match_inds = match_start_end_inds[match_ind]
        starting_ind_of_match = match_inds[0]
        end_ind_of_match_plus_1 = match_inds[1]
        string_matches.insert(0, text[starting_ind_of_match:end_ind_of_match_plus_1])
        text = text[:starting_ind_of_match] + placeholder_str + text[end_ind_of_match_plus_1:]
    # ideally, this would be more types of whitespace, but pig only does space in its TOKENIZE method
    tokenized_text = text.split(' ')
    match_inds = []
    num_matches_found_so_far = 0
    for i in range(len(tokenized_text)):
        while placeholder_str in tokenized_text[i]:
            match_inds.append(i)
            tokenized_text[i] = tokenized_text[i].replace(placeholder_str,
                                                          string_matches[num_matches_found_so_far], 1)
            num_matches_found_so_far += 1

    window_size = 30
    for i in range(len(match_inds)):
        match_ind = match_inds[i]
        start_start_ind = max([match_ind - window_size, 0])
        start_end_ind = match_ind
        end_start_ind = match_ind + 1
        end_end_ind = end_start_ind + window_size
        match_str = " ".join(tokenized_text[start_start_ind:start_end_ind] +
                             tokenized_text[end_start_ind:end_end_ind])
        bag_to_return.append((string_matches[i], match_str))
    return bag_to_return


@outputSchema("bag{tuple(searchterm:chararray, text:chararray)}")
def docmakingudfnonoverlapping(text):
    placeholder_str = '``````````````'
    try:
        text = text.decode('utf-8')
    except:
        text = str(text).strip()
        if text == '' or text == "None":
            return []

    false_match_inds = [(m.start(0), m.end(0)) for m in regexes_to_consider_false_matches.finditer(text)]
    match_start_end_inds = []
    for regex_to_search_for in regexes_to_search_for:
        new_inds = [(m.start(0), m.end(0)) for m in regex_to_search_for.finditer(text)]
        for i in range(len(new_inds) - 1, -1, -1):
            if text[new_inds[i][0] - 1].isalpha() or text[new_inds[i][1]].isalpha():
                del new_inds[i]
        inds_to_del = []
        for i in range(len(new_inds) - 1, -1, -1):
            for j in range(len(false_match_inds)):
                #assert i < len(new_inds), text
                if new_inds[i][0] >= false_match_inds[j][0] and new_inds[i][1] <= false_match_inds[j][1]:
                    inds_to_del.append(i)  # it's a false match
        for ind in inds_to_del:
            del new_inds[ind]
        new_list_pointer = 0
        big_list_pointer = 0
        while new_list_pointer < len(new_inds):
            if big_list_pointer >= len(match_start_end_inds):
                while new_list_pointer < len(new_inds):
                    match_start_end_inds.append(new_inds[new_list_pointer])
                    new_list_pointer += 1
                break
            else:
                if match_start_end_inds[big_list_pointer][0] >= new_inds[new_list_pointer][0]:
                    match_start_end_inds.insert(big_list_pointer, new_inds[new_list_pointer])
                    new_list_pointer += 1
            big_list_pointer += 1
    bag_to_return = []
    if len(match_start_end_inds) == 0:
        return bag_to_return
    string_matches = []
    for match_ind in range(len(match_start_end_inds) - 1, -1, -1):
        match_inds = match_start_end_inds[match_ind]
        starting_ind_of_match = match_inds[0]
        end_ind_of_match_plus_1 = match_inds[1]
        string_matches.insert(0, text[starting_ind_of_match:end_ind_of_match_plus_1])
        text = text[:starting_ind_of_match] + placeholder_str + text[end_ind_of_match_plus_1:]
    # ideally, this would be more types of whitespace, but pig only does space in its TOKENIZE method
    tokenized_text = text.split(' ')
    match_inds = []
    num_matches_found_so_far = 0
    for i in range(len(tokenized_text)):
        while placeholder_str in tokenized_text[i]:
            match_inds.append(i)
            tokenized_text[i] = tokenized_text[i].replace(placeholder_str,
                                                          string_matches[num_matches_found_so_far], 1)
            num_matches_found_so_far += 1

    window_size = 30
    prev_match_list_of_words_to_append_to = []
    prev_match_list_of_religious_terms_to_append_to = []
    for i in range(len(match_inds)):
        match_ind = match_inds[i]
        start_start_ind = max([match_ind - window_size, 0])
        if i > 0:
            # adjust start ind up to just past the previous match ind, if necessary
            start_start_ind = max([start_start_ind, match_inds[i - 1] + 1])
        start_end_ind = match_ind
        end_start_ind = match_ind + 1
        end_end_ind = end_start_ind + window_size
        prev_match_list_of_religious_terms_to_append_to.append(string_matches[i])
        if i < len(match_inds) - 1:
            next_match_window_start_ind = match_inds[i + 1] - window_size
            if end_end_ind > next_match_window_start_ind:
                # the matches overlap, so add less to this one
                if next_match_window_start_ind <= match_ind + 1:
                    # just add the words before this match, since the starting window for the next match
                    # will have this match's index (+1) as its starting point
                    prev_match_list_of_words_to_append_to += (tokenized_text[start_start_ind:start_end_ind])
                else:
                    # add the full set of words before this match, as well as some of the ones after it
                    prev_match_list_of_words_to_append_to += (tokenized_text[start_start_ind:start_end_ind] +
                                                              tokenized_text[end_start_ind:next_match_window_start_ind])
            else:
                prev_match_list_of_words_to_append_to += (tokenized_text[start_start_ind:start_end_ind] +
                                                          tokenized_text[end_start_ind:end_end_ind])
                bag_to_return.append(("_".join(prev_match_list_of_religious_terms_to_append_to),
                                      " ".join(prev_match_list_of_words_to_append_to)))
                prev_match_list_of_words_to_append_to = []
                prev_match_list_of_religious_terms_to_append_to = []
        else:
            # we're on the last match of the document, so don't bother resetting prev_match lists
            prev_match_list_of_words_to_append_to += (tokenized_text[start_start_ind:start_end_ind] +
                                                      tokenized_text[end_start_ind:end_end_ind])
            bag_to_return.append(("_".join(prev_match_list_of_religious_terms_to_append_to),
                                  " ".join(prev_match_list_of_words_to_append_to)))
    return bag_to_return

#doc = "hearing archives :committee on ways & means :: u.s. house of representatives : javascript is required for best results. click here to view committee proceedings live   health care reform h.r. 3962 affordable health care for america act as introduced h.r. 3961 medicare physician payment reform act of 2009  the american recovery and reinvestment plan   request for written comments on additional miscellaneous tariff and duty suspension bills h.r. 3548 unemployment compensation extension act of 2009 h.r. 7060,  renewable energy and job creation tax act of 2008  tax legislation in the 110th congress fact sheet on h.r. 3631, the medicare premium fairness act information on extending unemployment benefits h.r. 7327  pension relief and technical corrections    president signs schip bill into law president barack h. obama signs h. r. 2, the children s health insurance program reauthorization act on february 4, 2009 the american recovery and reinvestment act your money at work health care reform reforming health care is a necessary step in rebuilding our economy internship opportunities committee on ways and means internship opportunities   printer friendly version miller reporting company, inc   fifth in a series of hearings on social security number high-risk issues  hearing before  the subcommittee on social security of the committee on ways and means u.s. house of representatives one hundred ninth congress second session march 30, 2006 serial 109-62 printed for the use of the committee on ways and means         committee on ways and means bill thomas, california, chairman   e. clay shaw, jr., florida nancy l. johnson, connecticut wally herger, california jim mccrery, louisiana dave camp, michigan jim ramstad, minnesota jim nussle, iowa sam johnson, texas phil english, pennsylvania j.d. hayworth, arizona jerry weller, illinois kenny c. hulshof, missouri ron lewis, kentucky mark foley, florida kevin brady, texas thomas m. reynolds, new york paul ryan, wisconsin eric cantor, virginia john linder, georgia bob beauprez, colorado melissa a. hart, pennsylvania chris chocola, indiana devin nunes, california charles b. rangel, new york fortney pete stark, california sander m. levin, michigan benjamin l. cardin, maryland jim mcdermott, washington john lewis, georgia richard e. neal, massachusetts michael r. mcnulty, new york william j. jefferson, louisiana john s. tanner, tennessee xavier becerra, california lloyd doggett, texas earl pomeroy, north dakota stephanie tubbs jones, ohio mike thompson, california john b. larson, connecticut rahm emanuel, illinois     s ubcommittee on social security jim mccrery, louisiana, chairman     e. clay shaw, jr., florida sam johnson, texas j.d. hayworth, arizona kenny c. hulshof, missouri ron lewis, kentucky kevin brady, texas paul ryan, wisconsin sander m. levin, michigan earl pomeroy, north dakota xavier becerra, california stephanie tubbs jones, ohio richard e. neal, massachusetts     allison h. giles, chief of staff janice mays, minority chief counsel   pursuant to clause 2(e)(4) of rule xi of the rules of the house, public hearing records of the committee on ways and means are also published in electronic form. the printed hearing record remains the official version. because electronic submissions are used to prepare both printed and electronic versions of the hearing record, the process of converting between various electronic formats may introduce unintentional errors or omissions. such occurrences are inherent in the current publication process and should diminish as the process is further refined.             c o n t e n t s advisory of march 23, 2006 announcing the hearing witnesses the honorable david dreier, a representative in congress from the state of california the honorable silvestre reyes, a representative in congress from the state of texas federal trade commission, joel winston, associate director, division of privacy and identity protection, bureau of consumer protection, u.s. government accountability office, cynthia m. fagnoni, managing director, education, workforce, and income security bits fraud reduction steering committee, erik stein consumer data industry association, stuart k. pratt council of state court administrators, mary c. mcqueen identity theft resource center, nicole robinson national council of investigation and security services, bruce hulme submissions for the record kenney, john p., corona del mar, ca, letter sybesma, jamie, fishers, in, statement fifth in a series of hearings on social security number high-risk issues thursday, march 30, 2006 house of representatives, subcommittee on social security, committee on ways and means, washington, d.c.   the subcommittee met, pursuant to notice, at 2:40 p.m., in room b 318 rayburn house office building, hon. jim mccrery (chairman of the subcommittee) presiding.  [ the advisory announcing the hearing follow:] chairman mccrery.  the subcommittee hearing will come to order.  good afternoon, everybody.  welcome to our fifth in a series of hearings on high risk issues related to social security numbers (ssns).  today, we will examine the use of ssns by government agencies, businesses, and others, as well as explore options for improving the confidentiality of ssns. for many years, this subcommittee has worked to protect ssn privacy.  for example, the committee on ways and means approved bills in the 108th and 106th congresses that were introduced by my predecessor, subcommittee chairman clay shaw.  some of the provisions from mr. shaw's bill in the 108th congress have become law, including limits on replacement ssn cards and a prohibition on the display of ssns on drivers' licenses. the ssn plays a key role in both our government and in our economy.  since the ssn is a unique number for each person and is widely used, it helps link records at all levels.  this, in turn, facilitates administration of government services and benefits, business transactions, and fraud prevention.  however, once this essential piece of information is in the hands of identity thieves, it opens a pandora's box of problems.  stolen ssns can damage lives and businesses' bottom lines. today, we will hear about the current patchwork of federal and state laws that provide limited and inconsistent confidentiality protection for ssns.  for example, financial institutions are restricted in their ability to release ssn information, but ssns may appear in any number of publicly available government records, such as court records or property ownership records. computers and the internet have enabled unprecedented information sharing, and anyone who collects, uses, or shares ssn information has a responsibility to protect its confidentiality.  today, we will hear about some of the voluntary steps that government agencies, businesses, and others are taking to protect ssns from unauthorized disclosure.  we also will have the opportunity to explore options for improving ssn protections. these options involve complicated trade offs.  in some cases, federal laws and regulations require the collection of ssns to achieve certain goals, such as efficient and accurate tax administration, child support enforcement, and identification of money launderers and terrorists.  as we examine alternatives for improving ssn privacy to help prevent identity theft, we must consider the potential effect on the attainment of those goals.  we must also be mindful of the costs that individuals, businesses, and government agencies may incur as a result. by carefully examining all options to keep ssns out of the hands of identity thieves and by listening to as many stakeholders as possible, we seek a balance between protecting ssn privacy and allowing its use for legitimate and necessary purposes.mr. levin? mr. levin.  mr. chairman, since i basically agree with your opening statement and since both of our colleagues here, i would simply ask that my opening statement be placed in the record. chairman mccrery.  without objection.  thank you, mr. levin. [the prepared statement of mr. levin follows:] chairman mccrery.  our first panel today is composed of two distinguished colleagues, mr. dreier and mr. reyes, each of whom have expressed an interest in the issues that this subcommittee has been exploring for some time now.  they were supposed to be here last time, but we had a series of votes, and in an effort to not prolong the necessity for other witnesses to stay, we asked these two colleagues if they could come today, and they graciously agreed to do that. welcome, gentlemen.  we are interested in your views on this subject.  we would like for you to try to summarize those views in about 5 minutes, and we will start with my colleague from california, mr. dreier. statement of david dreier, a representative in congress from the state of california mr. dreier.  thank you very much, mr. chairman.  let me begin by expressing my appreciation to you for the hard work that you do in dealing with this issue of social security and the specific issue you are tackling right now, and to mr. levin and mr. johnson and mr. brady, i thank all of you for being here.  i know we have completed our votes on the floor, but this is a very important issue. mr. reyes and i have come together in a bipartisan way to deal with an issue that is getting a great deal of attention.  the issue is immigration reform and border security.  i don't know if any of you all recall that we dealt with that back in december and our colleagues in the other body are tackling that question right now, as to how they move ahead this week and next on this issue. virtually everything that we do focuses on the supply side of the immigration problem.  on border security, what is it that we did?  well, we talked about building a 700 mile wall.  we talked about dramatically increasing the size of the border patrol, a lot of things that are designed to stem the flow of people coming into this country illegally. what is it that we really haven't done?  we haven't spent much time and effort looking at why it is that they come to the united states of america.  that is why mr. reyes and i, with the encouragement of t.j. bonner, who is the president of the national border patrol council, which is the union of border patrol agents, said, let us not just look at the supply side.  let us focus on the demand side here. why is it that people come into this country illegally?  they come here, 98 percent of them, for one reason and one reason only.  they come here looking for a job.  they are looking to feed their families.  they are looking for economic opportunity.  we all know that.  of the 12 million people who are in this country illegally, we know that nearly all of them are here as productive members of society, working, paying taxes, doing things that need to be done in this country. we know that they are here illegally and there is a strong sense that we need to take action.  we need to take action to deal with it. right now, there are 94 different combinations of documents, including that flimsy little social security card that was first put into place in 1935, that has not been updated once since 1935, that are used for a potential employee to go to a potential employer and get a job  94 different combinations of documents, including a school id card, a library card.  what mr. reyes and i have come together to do is very simply to say, why don't we make an attempt to put into place a smart, counterfeit proof social security card with an algorithm strip on the back of it, an algorithm strip which would simply go in and look at the data that is already there.  no new data  the government would not get its hands on any new data at all. this counterfeit proof card  actually, i carry a counterfeit example of my counterfeit proof card, this is an old union 76 credit card and i have just put the social security on the top of the card.  i used t.j. bonner's picture, since this was his idea, and his photo is here, and you would have an algorithm strip on the back. someone is going in, mr. chairman, to look for a job.  the potential employer decides, i might want to hire this person.  they either swipe this card or call an 800 number.  they dial the 800 number and it goes into a databank which is simply taking the ssn, linking it with the u.s. department of homeland security (dhs), and the only information that would go out is yea or nay.  is this person a qualified worker or not a qualified worker? we put on the bottom of this that this is not a national id card.  i know that from testimony you all have had in the past, from your last hearing, i understood that real concern is raised about if it looks like a duck, walks like a duck, acts like a duck, talks like a duck, it may be a duck.  the fact is, this is not a national id card.  why?  the only utilization of this card will be for, number one, social security purposes, which are correct, and number two, applying for a new job. now, as i look around this room, i feel pretty sanguine that everybody here, including xavier becerra, will be reelected as they head towards this november election. mr. becerra.  is that an endorsement? mr. dreier.  you don't want my endorsement, xavier. [laughter.] that might jeopardize it, if you had my endorsement.  the fact is, only people looking, mr. chairman, for a new job would be required to carry this.  a senior citizen would never have to have a counterfeit proof social security card.  someone who is a small business man or woman would never have to have a counterfeit proof social security card. what we have got is we have got a situation where the magnet that draws people across the border is jobs, and if the thumbs down comes from this card from the databank that is already there, we in our legislation increase the penalty dramatically and we increase enforcement dramatically.  by 400 percent, we increase the penalty, from $10,000 to $50,000 for hiring, and we have a 5 year prison term, and we also increase by 10,000 the number of enforcement agents. now, you and i were talking yesterday about this and i know that everyone in this room pays their taxes simply because they are patriotic americans, but there may be some people out there who realize that the internal revenue service (irs) is there and that may be the reason that as april 15 approaches, they will be paying their taxes.  i know none of us are among those. similarly, if we were to see four or five high profile arrests due to people who were knowingly hiring those who are here illegally, i am convinced that we would see a great diminution of the number of hirings taking place.  i am convinced that we have, if not the panacea, we have the ability to look at what deals with 98 percent of the people who come here illegally to help us address this issue. mr. chairman, i think we have got a great opportunity to do something here and i am pleased that members of the hispanic caucus have joined.  again, it is a very, very bipartisan measure.  it is my hope that as we look at the issue of immigration reform, we will be able to recognize that this is better for the employer, easier for the business man or woman who is looking to hire someone, because they don't have to look at 94 different combinations of documents and they are free of responsibility once they have gotten a yea or nay on it.  it is going to help us deal with this very serious problem that we have of illegal immigration and finally see the social security administration (ssa) bring that flimsy little paper to which i was referring into the 21st century. thank you very much. chairman mccrery.  thank you, mr. dreier. [the prepared statement of mr. dreier follows:] chairman mccrery.  now, our colleague from texas, mr. reyes. statement of silvestre reyes, a representative in congress from the state of texas mr. reyes.  thank you, mr. chairman, mr. levin, fellow colleagues.  i am pleased to be here with my good friend and colleague from california, and i just want to make three points, but before i make those points, i want to tell you that in 1986, when the immigration control and reform act (p.l. 99-603) (irca) was passed, it had a provision for employer sanctions in there.  had congress provided the resources to ins, border patrol back then, we wouldn't be having the debates that we are having today. fast forward to 2006 and the three points that i want to make are that, as my colleague stated, the technology has gotten to the point where we feel very confident that a social security card with biometrics and algorithm and all the other things that have been mentioned were included, it would be safe to say  i always hesitate from the law enforcement background that something is counterfeit proof, but it would be very hard to replicate with the kind of technology that is available today.  you need that card that would, in essence, relieve any employer from the responsibility of having to look at and file as many as nine and ten documents, as the i 9 provision currently requires, with the fraud proof social security card. the second point i want to make is that along with that card, you need a system, a system where an employer, once he is presented with that card, can check and verify whether it is the individual.  if there is a question, they can ask somebody to come out and check it out or maybe check it out through the computer.  those systems exist today.  they are not cheap, but i would say they are a lot cheaper than all of these other proposals that have been  and not as controversial as the ones that have been proposed in the bill that we passed in december, the wall, taking citizenship, all these things that are very contentious. the third point i want to make is that adequate resources must be provided along with it.  no system is good if you don't provide the resources for checks.  you have got to provide the money.  you have got to provide the people.  our bill does that. those are the three basic points i wanted to make.  i have a statement that i would like to include into the record, but now, being respectful of your time, i will yield back the balance of my time, subject to any questions you might have for me or for my colleague. chairman mccrery.  thank you, mr. reyes. [the prepared statement of mr. reyes follows:] chairman mccrery.  both of your statements will be included in the record.  your written statements will be included in the record in their entirety. mr. dreier, you said the employer would either swipe the card or call an 800 number.  explain that.  what 800 number would they call? mr. dreier.  basically, what that would mean is that there would be a databank, the information, again, that the government already has, known information.  is someone an american citizen?  are they here on an h 2a visa, which is basically a farm worker visa, some other kind of work permit?  they would simply be told yes or no.  this person who is applying for a job to work in your company is, in fact, a qualified worker, and   chairman mccrery.  if you are an employer and you call this 800 number, what do you say? mr. dreier.  what you do is you provide the information that is there, the ssn, and obviously the goal would be to have a swipe for people so that they would be able to utilize the algorithm strip.  there would be a transition period, clearly, through which they would go that would--obviously, a big challenge   mr. reyes.  mr. chairman, if i can just add to that, if you don't mind   chairman mccrery.  sure. mr. reyes.  what happens today when you go into a restaurant or you go into a shop and you pay with a credit card, they put it into the system.  they swipe it or they insert it in the machine readable system.  if there is an issue or a problem that they think it may not be you or some other thing, then the merchant will call an 800 number and they will verify the account and all these other things. that is what we have in mind here.  remember, we are talking abou"
#print(docmakingudf(doc))