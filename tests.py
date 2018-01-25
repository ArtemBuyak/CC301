import unittest

from meter.crc import CRC16_C0C1


class TestCRC16_C0C1(unittest.TestCase):
    def test_correct_crc(self):
        """Проверяем для случая с заведомо правильной CRC"""
        count = 0   # проверено

        # Открываю входной файл

        input_file = open("test_data/test_correct.dat", "r")

        # читаю первую строку
        line = input_file.readline()

        # читаем до тех пор, пока не пойдут пустые строки
        while line != '':
            # чистим от ненужных знаков
            line = line.strip() #replace('\n', '')

            # строка с hex значениями в байтстроку
            hex_int_list = []

            # разделяем на отдельные значения
            hex_str_list = line.split(' ')

            # сохраняем в новый списос, приводя к int
            for hex_entry in hex_str_list:
                hex_int_list.append(int(hex_entry ,16))

            # создаем экземпляр класса CRC
            crc_obj = CRC16_C0C1()

            # проверяем
            self.assertEqual(
                crc_obj.check(buffer=bytes(hex_int_list), count=len(bytes(hex_int_list))-2),
                True
            )

            # читаем новую строку
            line = input_file.readline()

            count = count + 1

        print("Messages processed {}".format(count))
        input_file.close()

    def test_bad_crc(self):
        """Проверяем для случая с заведомо неправильной CRC"""
        count = 0   # проверено

        # Открываю входной файл

        input_file = open("test_data/test_bad.dat", "r")

        # читаю первую строку
        line = input_file.readline()

        # читаем до тех пор, пока не пойдут пустые строки
        while line != '':
            # чистим от ненужных знаков
            line = line.strip() #replace('\n', '')

            # строка с hex значениями в байтстроку
            hex_int_list = []

            # разделяем на отдельные значения
            hex_str_list = line.split(' ')

            # сохраняем в новый списос, приводя к int
            for hex_entry in hex_str_list:
                hex_int_list.append(int(hex_entry ,16))

            # создаем экземпляр класса CRC
            crc_obj = CRC16_C0C1()

            # проверяем
            self.assertEqual(
                crc_obj.check(buffer=bytes(hex_int_list), count=len(bytes(hex_int_list))-2),
                False
            )

            count = count + 1

            # читаем новую строку
            line = input_file.readline()

        print("Messages processed {}".format(count))
        input_file.close()


if __name__ == '__main__':
    unittest.main()