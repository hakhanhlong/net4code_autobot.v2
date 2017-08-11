from ultils import stringhelpers



def main():
    string_results = 'Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5'
    start_by = 'Retransmit'
    end_by = ''

    print(stringhelpers.find_between(string_results, start_by, end_by))



    print(string_results.find(start_by) + len(start_by))
    print(len(string_results))

    print(string_results[string_results.find(start_by) + len(start_by):len(string_results)])




if __name__ == '__main__':
    main()
