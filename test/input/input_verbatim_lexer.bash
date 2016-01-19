# sourcing code detection, if code is sourced for debug purpose, main is not executed.
[[ $0 != "$BASH_SOURCE" ]] && sourced=1 || sourced=0
if  [[ $sourced -eq 0 ]]
then
    # pass positional argument as is
    main "$@"
fi
# libido: }
