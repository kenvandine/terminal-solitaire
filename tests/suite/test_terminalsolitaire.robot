*** Settings ***
Documentation    Test cases for terminal-solitaire snap
Resource         kvm.resource
Library          Process


*** Test Cases ***
Terminal Solitaire Launches And Renders
    [Documentation]    Verify terminal-solitaire snap launches in a foot terminal on Mir
    [Tags]    smoke    yarf:certification_status: blocker
    Start Process    /usr/bin/foot    snap    run    terminal-solitaire    alias=terminal-solitaire
    Sleep    3s
    Log Screenshot
    [Teardown]    Terminate Process    terminal-solitaire
