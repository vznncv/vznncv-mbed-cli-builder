import mbed.mbed

# drop support of non-git VCS
for k in list(mbed.mbed.scms):
    if k != 'git':
        mbed.mbed.scms.pop(k)

mbed.mbed.main()
