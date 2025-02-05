from pathlib import Path
import json

# TODO add cybench and htb challenges
chals = {"nyuctf": ["2021f-cry-interoperable", "2021f-cry-ibad", "2021f-cry-collision_course", "2021q-cry-bits", "2021q-cry-gotta_decrypt_them_all", "2021q-cry-crack_me", "2021q-cry-rsa_pop_quiz", "2021q-cry-ecc_pop_quiz", "2021q-cry-forgery", "2020f-cry-eccentric", "2020f-cry-hybrid2", "2020f-cry-the_matrix", "2020f-cry-jackpot", "2020q-cry-authy", "2020q-cry-difib", "2020q-cry-perfect_secrecy", "2020q-cry-adversarial", "2020q-cry-smallsurp", "2020q-cry-modus_operandi", "2022f-cry-open_ellipti_ph", "2022f-cry-polly_crack_this", "2022f-cry-m_ster_0f_prn9", "2022f-cry-the_lengths_we_extend_ourselves", "2022q-cry-beyond_quantum", "2022q-cry-too_much_in_common", "2022q-cry-gift_shop", "2022q-cry-gotta_crack_them_all", "2022q-cry-not_too_taxing", "2023f-cry-nervcenter", "2023f-cry-textbook_rsa", "2023f-cry-describeme", "2023q-cry-mental_poker", "2023q-cry-circles", "2023q-cry-lottery", "2019f-cry-macrypto", "2019q-cry-des2bites", "2019q-cry-brillouin", "2019q-cry-count_on_me", "2019q-cry-super_curve", "2019q-cry-byte_me", "2017f-cry-ecxor", "2017f-cry-lupin", "2017q-cry-another_xor", "2017q-cry-baby_crypt", "2017q-cry-almost_xor", "2018f-cry-asr4cr", "2018f-cry-lost_mind", "2018f-cry-distastrous_security_apparatus", "2018q-cry-lowe", "2018q-cry-collusion", "2018q-cry-babycrypto", "2018q-cry-flatcrypt", "2021f-for-no_time_to_register", "2021f-for-constela", "2021q-for-lazy_leaks", "2023f-for-forensings", "2023f-for-hypokrinesthai", "2023f-for-floating_points", "2023f-for-ancient_forensics", "2023f-for-emoji", "2023q-for-br3akth3vau1t", "2023q-for-1black0white", "2017f-for-thoroughlystripped", "2017q-for-missed_registration", "2017q-for-best_router", "2018q-for-simple_recovery", "2018q-for-whyos", "2021f-pwn-horrorscope", "2021f-pwn-chatterbox", "2021q-pwn-krypto", "2021q-pwn-alien_math", "2021q-pwn-password_checker", "2021q-pwn-haystack", "2020f-pwn-darkunion1", "2020q-pwn-thebardsfail", "2020q-pwn-slithery", "2020q-pwn-grid", "2020q-pwn-feather", "2020q-pwn-blox2", "2020q-pwn-pwnvoltex", "2020q-pwn-roppity", "2022f-pwn-salt_server", "2022f-pwn-cryptopwn", "2022q-pwn-ezrop", "2022q-pwn-unsafe_linking", "2023f-pwn-virtualization_pwn", "2023f-pwn-brainflop", "2023q-pwn-unlimited_subway", "2023q-pwn-target_practice", "2023q-pwn-puffin", "2023q-pwn-my_first_pwnie", "2019f-pwn-arevenge", "2019q-pwn-pop_goes_the_printer", "2019q-pwn-got_milk", "2019q-pwn-popping_caps_2", "2019q-pwn-popping_caps", "2019q-pwn-small_boi", "2019q-pwn-baby_boi", "2019q-pwn-traveller", "2017f-pwn-humm_sch_t", "2017q-pwn-pilot", "2017q-pwn-zone", "2018f-pwn-es1337", "2018q-pwn-shellpointcode", "2018q-pwn-bigboy", "2018q-pwn-get_it", "2021f-rev-maze", "2021f-rev-sfc", "2021q-rev-ransomware", "2021q-rev-macomal", "2021q-rev-ncore", "2021q-rev-checker", "2020f-rev-rap", "2020f-rev-brrr", "2020f-rev-yeet", "2020f-rev-sourcery", "2020q-rev-not_malware", "2020q-rev-ezbreezy", "2020q-rev-baby_mult", "2022f-rev-roulette", "2022f-rev-parallel_vm", "2022q-rev-dockreleakage", "2022q-rev-game",
         "2022q-rev-anyagacha", "2022q-rev-the_big_bang", "2023f-rev-unvirtualization", "2023f-rev-cell", "2023f-rev-virtualization", "2023q-rev-whataxor", "2023q-rev-baby_s_first", "2023q-rev-rox", "2023q-rev-rebug_2", "2023q-rev-baby_s_third", "2023q-rev-rebug_1", "2019f-rev-wrangly", "2019f-rev-mystery_boi", "2019f-rev-steady_counting", "2019q-rev-beleaf", "2019q-rev-call_site", "2019q-rev-gibberish_check", "2019q-rev-halfpike", "2019q-rev-wizkid", "2017f-rev-48_bit_yeet_lab", "2017f-rev-rusty_road", "2017f-rev-rabbithole", "2017q-rev-bananascript", "2017q-rev-tablez", "2017q-rev-realism", "2017q-rev-grumpcheck", "2017q-rev-prophecy", "2017q-rev-gopherz", "2018f-rev-free_as_in_freedom", "2018f-rev-bdos", "2018f-rev-1nsayne", "2018q-rev-a_walk_through_x86_part_2", "2018q-rev-kvm", "2018q-rev-a_walk_through_x86_part_1", "2021q-web-no_pass_needed", "2021q-web-poem_collection", "2021q-web-securinotes", "2021q-web-gatekeeping", "2021q-web-scp_terminal", "2020f-web-snailrace1", "2020f-web-picgram", "2020f-web-sharkfacts", "2023f-web-shreeramquest", "2023f-web-triathlon_or_sprint", "2023q-web-cookie_injection", "2023q-web-philanthropy", "2023q-web-rainbow_notes", "2023q-web-smug_dino", "2019f-web-biometric", "2017q-web-littlequery", "2017q-web-orangev2", "2017q-web-orange", "2017q-web-notmycupofcoffe", "2021f-msc-terminal_velocity", "2021q-msc-weak_password", "2021q-msc-save_the_tristate", "2022f-msc-farmlang", "2022f-msc-embrey0_leak", "2022f-msc-super_guesser_g_me", "2022q-msc-quantum_leap", "2022q-msc-ezmaze", "2022q-msc-cattheflag", "2023f-msc-pyjail", "2023f-msc-vectors_machine", "2023f-msc-urkel", "2023f-msc-sigmaslogistics", "2023q-msc-android_dropper", "2023q-msc-tradinggame", "2023q-msc-linear_aggressor", "2019f-msc-alive", "2017q-msc-cvv", "2017q-msc-serial", "2018f-msc-showdown", "2018f-msc-leaked_flag", "2018q-msc-short_circuit", "2018q-msc-bin_t", "2018q-msc-algebra"]}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Print results for logs")
    parser.add_argument("--logdir", required=True)
    parser.add_argument("--dataset", default="nyuctf", choices=["nyuctf", "cybench", "htb"])
    args = parser.parse_args()
    
    logdir = Path(args.logdir)
    success_count=0
    error_count=0
    failed_count=0
    total_count=0
    for chal in chals[args.dataset]:
        chalf = logdir / f"{chal}.json"
        print(chal, end="\t")
        if not chalf.exists():
            print("")
            continue

        chaldata = json.loads(chalf.open().read())
        total_count+=1

        if chaldata["success"]:
            success_count+=1
            print("1")
        elif chaldata["error"]:
            error_count+=1
            print("error")
        else:
            failed_count+=1
            print("0")

    print("total_count:",total_count)
    print("success_count:",success_count)
    print("error_count:",error_count)
    print("failed_count:",failed_count)