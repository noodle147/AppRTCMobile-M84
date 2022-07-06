from os.path import exists, isfile, realpath, dirname, join, isdir
from os import listdir, makedirs, remove
import shutil
import sys

KEY_SUCCESS = "success"
KEY_MESSAGE = "message"
KEY_PATH_WEBRTC_SRC = "-webrtc_src="
KEY_PATH_BUILD_GRADLE = "-build_gradle="
KEY_PATH_OUTPUT = "-output="

def print_help():
    return


def parse_args():
    result = {}
    if len(sys.argv) != 3:
        print_help()
        result[KEY_SUCCESS] = False
        result[KEY_MESSAGE] = "argument's count incorrect"
        return result

    for arg in sys.argv[1:] :
        if arg.startswith(KEY_PATH_WEBRTC_SRC):
            result[KEY_PATH_WEBRTC_SRC] = arg[len(KEY_PATH_WEBRTC_SRC):]
        elif arg.startswith(KEY_PATH_OUTPUT):
            result[KEY_PATH_OUTPUT] = arg[len(KEY_PATH_OUTPUT):]
        elif arg.startswith(KEY_PATH_BUILD_GRADLE):
            result[KEY_PATH_BUILD_GRADLE] = arg[len(KEY_PATH_BUILD_GRADLE):]
        else:
            result[KEY_SUCCESS] = False
            result[KEY_MESSAGE] = "unknown argument " + arg
            return result

    keys = (KEY_PATH_BUILD_GRADLE, KEY_PATH_OUTPUT)
    for key in keys:
        if result.get(key) == None:
            result[KEY_SUCCESS] = False
            result[KEY_MESSAGE] = "missing argument " + key
            return result

    result[KEY_SUCCESS] = True
    result[KEY_MESSAGE] = "success"
    return result


def checkPath(paths):
    # if not exists(paths[KEY_PATH_WEBRTC_SRC]):
    #     print("webrtc src path not exist: " + paths[KEY_PATH_WEBRTC_SRC])
    #     return False

    if not exists(paths[KEY_PATH_BUILD_GRADLE]):
        print("build gradle path not exist: " + paths[KEY_PATH_BUILD_GRADLE])
        return False
    
    if not isfile(paths[KEY_PATH_BUILD_GRADLE]):
        print("build gradle path is not a file: " + paths[KEY_PATH_BUILD_GRADLE])
        return False

    if not exists(paths[KEY_PATH_OUTPUT]):
        print("output path not exist")
        # print("output path not exist, creating")
        # makedirs(paths[KEY_PATH_OUTPUT])

    return True


def copy(src, dest):
    if not exists(src):
        print("source {} not exist".format(src))
        return
    
    if isfile(src):
        print("cp {} \n=> {}".format(src, dest))
        shutil.copy(src, dest)
        return
    
    subs = listdir(src)
    for sub in subs:
        srcPath = join(src, sub)
        destPath = join(dest, sub)
        if isdir(srcPath):
            if not exists(destPath):
                print("mkdir {}".format(destPath))
                makedirs(destPath)
            # print("copy sub directory from {} to {}".format(srcPath, destPath))
            copy(srcPath, destPath)
        elif isfile(srcPath):
            # print("copy file from {} to {}".format(srcPath, destPath))
            copy(srcPath, destPath)
        else:
            print("!!!Should not be here!!!")

    return


def process_build_gradle(path_build_gradle, path_output):
    dirBuildGradle = dirname(realpath(path_build_gradle))
    print("directory of build gradle {}".format(dirBuildGradle))

    file = open(path_build_gradle, 'r')
    lines = file.readlines()
    len(lines)
    index = 0
    beginFilter = False
    endFilter = False
    for line in lines:
        index += 1

        if line.lstrip().startswith("java.srcDirs += \'") or line.lstrip().startswith("java.srcDirs += \""):
            srcDir = realpath(join(dirBuildGradle, line.lstrip().rstrip()[17:-1]))
            print("directory of java src {}, copying to {}".format(srcDir, path_output))
            copy(srcDir, path_output)
            continue

        if line.lstrip().startswith("java.filter.exclude(["):
            beginFilter = True
            print("begin filter")
            continue

        if beginFilter and not line.lstrip().startswith("\""):
            endFilter = True
            print("end filter")
            break

        if beginFilter and not endFilter:
            path = realpath(join(path_output, line.lstrip().rstrip()[1:-2]))
            if path.endswith("*.java"):
                dir = dirname(path)
                print("del *.java under {}".format(dir))
                files = listdir(dir)
                print("files {}".format(files))
                for file in files:
                    if file.endswith(".java"):
                        fullpath = realpath(join(dir, file))
                        print("del {}".format(fullpath))
                        remove(fullpath)
            else:
                print("del {}".format(path))
                remove(path)

    return

def main():
    result = parse_args()

    if(not result[KEY_SUCCESS]):
        print(result[KEY_MESSAGE])
        exit(-1)

    if not checkPath(result):
        exit(-1)
    
    process_build_gradle(result[KEY_PATH_BUILD_GRADLE], result[KEY_PATH_OUTPUT])
    return

main()


