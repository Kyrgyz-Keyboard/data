import apertium

apertium.windows_update_path()
# apertium.installer.install_apertium()
apertium.installer.install_module('eng')

a = apertium.Analyzer('en')

print(a.analyze('cats'))

a = apertium.Analyzer('kir')

print(a.analyze('кыйынчылыктардан')[0])
