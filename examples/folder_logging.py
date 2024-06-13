from kva import kva, Folder


kva.init(run_id="Current CWD")

kva.log(cwd=Folder('examples'))

kva.log(cwd=Folder('kva'))

merged_folder = kva.get(run_id="Current CWD").latest('cwd')

src_folder = kva.get(run_id="Current CWD").latest('cwd', deep_merge=False)